from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

ComfortLevel = Literal["economy_comfort", "balanced", "premium_comfort"]

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - optional runtime dependency
    FastMCP = None  # type: ignore[assignment]

mcp = FastMCP("travel-planner-agent") if FastMCP is not None else None


@dataclass
class ComfortPreference:
    max_flight_hours: float
    allow_red_eye: bool
    max_transfers: int
    hotel_stars_min: int
    daily_pace: Literal["relaxed", "moderate"]
    food_requirements: List[str] = field(default_factory=list)


@dataclass
class TravelRequest:
    destination: str
    origin: str
    days: int
    travelers: int
    total_budget: float
    comfort: ComfortPreference

    def validate(self) -> None:
        if not self.destination.strip():
            raise ValueError("destination is required")
        if not self.origin.strip():
            raise ValueError("origin is required")
        if self.days < 2:
            raise ValueError("days must be >= 2")
        if self.travelers < 1:
            raise ValueError("travelers must be >= 1")
        if self.total_budget <= 0:
            raise ValueError("total_budget must be > 0")
        if self.comfort.hotel_stars_min < 2:
            raise ValueError("hotel_stars_min must be >= 2")
        if self.comfort.max_transfers < 0:
            raise ValueError("max_transfers must be >= 0")
        if self.comfort.max_flight_hours <= 0:
            raise ValueError("max_flight_hours must be > 0")


class TravelPlannerAgent:
    """A heuristic travel planner that optimizes for comfort under budget limits."""

    BUDGET_BUCKETS = {
        "transport": 0.35,
        "hotel": 0.35,
        "food": 0.15,
        "tickets": 0.10,
        "buffer": 0.05,
    }

    PROFILES: Dict[ComfortLevel, Dict[str, Any]] = {
        "economy_comfort": {
            "hotel_stars_min": 3,
            "max_daily_moves": 3,
            "rest_block_hours": 1,
            "direct_flight_bonus": 0.05,
        },
        "balanced": {
            "hotel_stars_min": 4,
            "max_daily_moves": 2,
            "rest_block_hours": 2,
            "direct_flight_bonus": 0.08,
        },
        "premium_comfort": {
            "hotel_stars_min": 4,
            "max_daily_moves": 2,
            "rest_block_hours": 3,
            "direct_flight_bonus": 0.12,
        },
    }

    def create_plan_options(self, req: TravelRequest) -> Dict[str, Any]:
        req.validate()

        options: Dict[str, Dict[str, Any]] = {}
        for level in ("economy_comfort", "balanced", "premium_comfort"):
            options[level] = self._build_single_option(req, level)  # type: ignore[arg-type]

        options = self._add_upgrade_costs(options)
        return {
            "input_summary": self._input_summary(req),
            "options": options,
        }

    def replan(self, req: TravelRequest, current_plan: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
        kind = event.get("type", "")
        value = event.get("value")

        if kind == "budget_change" and isinstance(value, (int, float)):
            req.total_budget = float(value)
        elif kind == "weather_change":
            current_plan.setdefault("notes", []).append("天气变化：优先替换户外项目为室内活动。")
        elif kind == "temporary_cancellation":
            current_plan.setdefault("notes", []).append("临时取消：启用同区域低移动替代活动并重排时间。")

        req.validate()
        fresh = self.create_plan_options(req)
        fresh["replan_event"] = event
        return fresh

    def _build_single_option(self, req: TravelRequest, level: ComfortLevel) -> Dict[str, Any]:
        profile = self.PROFILES[level]
        comfort_floor_stars = max(req.comfort.hotel_stars_min, profile["hotel_stars_min"])

        budget = self._allocate_budget(req.total_budget, level)
        transport = self._choose_transport(req, profile)
        hotel = self._choose_hotel(req, comfort_floor_stars, budget["hotel"]["estimated"])
        itinerary = self._generate_daily_timeline(req, profile)

        total_estimated = sum(bucket["estimated"] for bucket in budget.values())
        over_budget = total_estimated > req.total_budget

        return {
            "name": level,
            "comfort_rules": {
                "flight": {
                    "prefer_direct": True,
                    "max_hours": req.comfort.max_flight_hours,
                    "max_transfers": min(req.comfort.max_transfers, 1),
                },
                "hotel": {"stars_min": comfort_floor_stars},
                "daily_pacing": {
                    "max_moves": profile["max_daily_moves"],
                    "rest_block_hours": profile["rest_block_hours"],
                },
            },
            "major_bookings": {
                "transport": transport,
                "hotel": hotel,
            },
            "daily_timeline": itinerary,
            "cost_breakdown": budget,
            "total_estimated": round(total_estimated, 2),
            "budget_cap": round(req.total_budget, 2),
            "over_budget": over_budget,
            "alternatives": self._overspend_alternatives(over_budget),
            "booking_checklist": [
                "确认往返交通并锁定可退改条件",
                f"预订至少{comfort_floor_stars}星酒店，优先核心交通区",
                "预订热门景点时段票",
                "准备境外保险/紧急联系人/证件复印件",
            ],
            "notes": self._notes(req),
            "emergency_plan": {
                "medical": "记录目的地急救电话与最近医院位置",
                "transport_disruption": "航班延误时优先改签直飞/高铁并保留休息时段",
                "budget_buffer_use": "仅用于突发交通和医疗支出",
            },
        }

    def _allocate_budget(self, total_budget: float, level: ComfortLevel) -> Dict[str, Dict[str, Any]]:
        multiplier = {
            "economy_comfort": {"transport": 0.95, "hotel": 0.95, "food": 1.0, "tickets": 1.0, "buffer": 1.0},
            "balanced": {"transport": 1.0, "hotel": 1.0, "food": 1.0, "tickets": 1.0, "buffer": 1.0},
            "premium_comfort": {"transport": 1.1, "hotel": 1.12, "food": 1.05, "tickets": 1.0, "buffer": 1.0},
        }[level]

        output: Dict[str, Dict[str, Any]] = {}
        for bucket, ratio in self.BUDGET_BUCKETS.items():
            estimated = total_budget * ratio * multiplier[bucket]
            output[bucket] = {
                "ratio": ratio,
                "estimated": round(estimated, 2),
            }
        return output

    def _choose_transport(self, req: TravelRequest, profile: Dict[str, Any]) -> Dict[str, Any]:
        direct_first = req.comfort.max_transfers == 0 or profile["direct_flight_bonus"] > 0.07
        return {
            "strategy": "优先直飞" if direct_first else "最多1次中转",
            "max_flight_hours": req.comfort.max_flight_hours,
            "max_transfers": min(req.comfort.max_transfers, 1),
            "red_eye_allowed": req.comfort.allow_red_eye,
        }

    def _choose_hotel(self, req: TravelRequest, stars: int, hotel_budget: float) -> Dict[str, Any]:
        per_night = round(hotel_budget / max(req.days - 1, 1), 2)
        return {
            "stars_min": stars,
            "target_nightly_budget": per_night,
            "location_rule": "距主要景点或交通枢纽30分钟内",
            "comfort_rule": "含早餐或附近步行可达餐饮",
        }

    def _generate_daily_timeline(self, req: TravelRequest, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        timeline: List[Dict[str, Any]] = []
        for day in range(1, req.days + 1):
            if day == 1:
                blocks = ["到达与入住", "轻量周边散步", "晚餐后休息"]
            elif day == req.days:
                blocks = ["退房与行李安排", "返程交通", "行程结束"]
            else:
                blocks = [
                    "上午1个核心景点",
                    f"午间休息{profile['rest_block_hours']}小时",
                    "下午1个低强度活动",
                    "晚间自由活动",
                ]

            timeline.append(
                {
                    "day": day,
                    "max_moves": profile["max_daily_moves"],
                    "activities": blocks,
                }
            )
        return timeline

    @staticmethod
    def _overspend_alternatives(over_budget: bool) -> List[str]:
        if not over_budget:
            return ["预算可控：可将机动金保留为应急。"]
        return [
            "交通降级：改为错峰航班但保持直飞优先",
            "住宿降级：核心地段4星改为口碑3-4星",
            "门票优化：高价项目改为半日/联票",
        ]

    @staticmethod
    def _notes(req: TravelRequest) -> List[str]:
        notes = [
            "先锁定大交通与酒店，再细化每日活动。",
            "每天控制移动次数，避免连续高强度行程。",
        ]
        if req.comfort.food_requirements:
            notes.append(f"饮食偏好：{', '.join(req.comfort.food_requirements)}")
        return notes

    @staticmethod
    def _input_summary(req: TravelRequest) -> Dict[str, Any]:
        return {
            "destination": req.destination,
            "origin": req.origin,
            "days": req.days,
            "travelers": req.travelers,
            "budget": req.total_budget,
            "comfort_preferences": {
                "max_flight_hours": req.comfort.max_flight_hours,
                "allow_red_eye": req.comfort.allow_red_eye,
                "max_transfers": req.comfort.max_transfers,
                "hotel_stars_min": req.comfort.hotel_stars_min,
                "daily_pace": req.comfort.daily_pace,
                "food_requirements": req.comfort.food_requirements,
            },
        }

    @staticmethod
    def _add_upgrade_costs(options: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        eco = options["economy_comfort"]["total_estimated"]
        balanced = options["balanced"]["total_estimated"]
        premium = options["premium_comfort"]["total_estimated"]

        options["economy_comfort"]["upgrade_cost_to_balanced"] = round(balanced - eco, 2)
        options["balanced"]["upgrade_cost_to_premium"] = round(premium - balanced, 2)
        options["premium_comfort"]["upgrade_cost_from_balanced"] = round(premium - balanced, 2)
        return options


def _request_from_dict(payload: Dict[str, Any]) -> TravelRequest:
    comfort_payload = payload.get("comfort")
    if not isinstance(comfort_payload, dict):
        raise ValueError("comfort must be an object")

    return TravelRequest(
        destination=str(payload.get("destination", "")),
        origin=str(payload.get("origin", "")),
        days=int(payload.get("days", 0)),
        travelers=int(payload.get("travelers", 0)),
        total_budget=float(payload.get("total_budget", 0)),
        comfort=ComfortPreference(
            max_flight_hours=float(comfort_payload.get("max_flight_hours", 0)),
            allow_red_eye=bool(comfort_payload.get("allow_red_eye", False)),
            max_transfers=int(comfort_payload.get("max_transfers", 0)),
            hotel_stars_min=int(comfort_payload.get("hotel_stars_min", 0)),
            daily_pace=str(comfort_payload.get("daily_pace", "moderate")),  # type: ignore[arg-type]
            food_requirements=list(comfort_payload.get("food_requirements", [])),
        ),
    )


def process_travel_request(input_text: str) -> str:
    payload = json.loads(input_text)
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")

    request_payload = payload.get("request", payload)
    if not isinstance(request_payload, dict):
        raise ValueError("request must be a JSON object")

    planner = TravelPlannerAgent()
    request = _request_from_dict(request_payload)

    if "event" in payload:
        event = payload.get("event")
        if not isinstance(event, dict):
            raise ValueError("event must be a JSON object")
        current_plan = payload.get("current_plan", {})
        if not isinstance(current_plan, dict):
            raise ValueError("current_plan must be a JSON object")
        result = planner.replan(request, current_plan, event)
    else:
        result = planner.create_plan_options(request)

    return json.dumps(result, ensure_ascii=False)


if mcp is not None:

    @mcp.tool()
    def plan_travel(input: str) -> str:
        """根据行程输入生成舒适度优先且预算可控的旅行计划，支持重规划事件。"""
        return process_travel_request(input)


def _demo_request() -> TravelRequest:
    return TravelRequest(
        destination="东京",
        origin="上海",
        days=5,
        travelers=2,
        total_budget=16000,
        comfort=ComfortPreference(
            max_flight_hours=4.0,
            allow_red_eye=False,
            max_transfers=0,
            hotel_stars_min=3,
            daily_pace="moderate",
            food_requirements=["海鲜过敏", "少辣"],
        ),
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        if mcp is None:
            raise SystemExit("MCP runtime not available. Please install package: mcp")
        mcp.run()
    else:
        planner = TravelPlannerAgent()
        plan = planner.create_plan_options(_demo_request())
        print(json.dumps(plan, ensure_ascii=False, indent=2))
