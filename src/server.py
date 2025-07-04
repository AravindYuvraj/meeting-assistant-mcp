#!/usr/bin/env python3
"""
Smart Meeting Assistant MCP Server
Manages meetings and calendars with AI-powered features
"""

import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import random
import statistics
from enum import Enum

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

# Data models
@dataclass
class TimeSlot:
    start: datetime
    end: datetime
    timezone: str = "UTC"

@dataclass
class User:
    id: str
    name: str
    email: str
    timezone: str
    work_hours: Dict[str, List[str]]  # day -> [start_time, end_time]
    preferences: Dict[str, Any]

@dataclass
class Meeting:
    id: str
    title: str
    participants: List[str]
    start_time: datetime
    end_time: datetime
    timezone: str
    organizer: str
    agenda: List[str]
    meeting_type: str
    recurring: bool = False
    effectiveness_score: Optional[float] = None
    created_at: datetime = None

class MeetingType(Enum):
    STANDUP = "standup"
    REVIEW = "review"
    PLANNING = "planning"
    BRAINSTORM = "brainstorm"
    ONE_ON_ONE = "one_on_one"
    PRESENTATION = "presentation"
    TRAINING = "training"

class SmartMeetingAssistant:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.meeting_templates: Dict[str, List[str]] = {}
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample users and meetings"""
        # Sample users with different timezones
        sample_users = [
            User(
                id="user_1", name="Alice Johnson", email="alice@company.com",
                timezone="America/New_York",
                work_hours={"monday": ["09:00", "17:00"], "tuesday": ["09:00", "17:00"],
                          "wednesday": ["09:00", "17:00"], "thursday": ["09:00", "17:00"],
                          "friday": ["09:00", "17:00"]},
                preferences={"max_meetings_per_day": 6, "preferred_meeting_length": 30,
                           "no_meeting_times": ["12:00-13:00"]}
            ),
            User(
                id="user_2", name="Bob Smith", email="bob@company.com",
                timezone="Europe/London",
                work_hours={"monday": ["08:00", "16:00"], "tuesday": ["08:00", "16:00"],
                          "wednesday": ["08:00", "16:00"], "thursday": ["08:00", "16:00"],
                          "friday": ["08:00", "16:00"]},
                preferences={"max_meetings_per_day": 5, "preferred_meeting_length": 45,
                           "no_meeting_times": ["11:30-12:30"]}
            ),
            User(
                id="user_3", name="Carol Davis", email="carol@company.com",
                timezone="Asia/Tokyo",
                work_hours={"monday": ["09:00", "18:00"], "tuesday": ["09:00", "18:00"],
                          "wednesday": ["09:00", "18:00"], "thursday": ["09:00", "18:00"],
                          "friday": ["09:00", "18:00"]},
                preferences={"max_meetings_per_day": 4, "preferred_meeting_length": 60,
                           "no_meeting_times": ["12:00-13:00"]}
            ),
            User(
                id="user_4", name="David Wilson", email="david@company.com",
                timezone="America/Los_Angeles",
                work_hours={"monday": ["08:00", "17:00"], "tuesday": ["08:00", "17:00"],
                          "wednesday": ["08:00", "17:00"], "thursday": ["08:00", "17:00"],
                          "friday": ["08:00", "17:00"]},
                preferences={"max_meetings_per_day": 7, "preferred_meeting_length": 30,
                           "no_meeting_times": ["13:00-14:00"]}
            ),
            User(
                id="user_5", name="Emma Brown", email="emma@company.com",
                timezone="Australia/Sydney",
                work_hours={"monday": ["09:00", "17:00"], "tuesday": ["09:00", "17:00"],
                          "wednesday": ["09:00", "17:00"], "thursday": ["09:00", "17:00"],
                          "friday": ["09:00", "17:00"]},
                preferences={"max_meetings_per_day": 5, "preferred_meeting_length": 45,
                           "no_meeting_times": ["12:00-13:00"]}
            )
        ]
        
        for user in sample_users:
            self.users[user.id] = user
        
        # Generate 60+ sample meetings
        self.generate_sample_meetings()
        
        # Meeting templates for agenda generation
        self.meeting_templates = {
            "standup": [
                "What did you accomplish yesterday?",
                "What are you working on today?",
                "Any blockers or challenges?",
                "Team updates and announcements"
            ],
            "review": [
                "Review previous action items",
                "Discuss project progress",
                "Identify risks and issues",
                "Plan next steps",
                "Assign action items"
            ],
            "planning": [
                "Define project scope and objectives",
                "Identify key deliverables",
                "Estimate timelines and resources",
                "Assign responsibilities",
                "Set milestones and checkpoints"
            ],
            "brainstorm": [
                "Problem statement review",
                "Idea generation session",
                "Evaluate and prioritize ideas",
                "Action plan development",
                "Next steps and ownership"
            ],
            "one_on_one": [
                "Performance and goal review",
                "Current project discussion",
                "Career development topics",
                "Feedback and concerns",
                "Action items and follow-ups"
            ]
        }
    
    def generate_sample_meetings(self):
        """Generate 60+ sample meetings with realistic distribution"""
        meeting_types = list(MeetingType)
        titles = {
            MeetingType.STANDUP: ["Daily Standup", "Team Sync", "Morning Check-in"],
            MeetingType.REVIEW: ["Sprint Review", "Project Review", "Quarterly Review"],
            MeetingType.PLANNING: ["Sprint Planning", "Project Planning", "Strategic Planning"],
            MeetingType.BRAINSTORM: ["Innovation Session", "Problem Solving", "Creative Workshop"],
            MeetingType.ONE_ON_ONE: ["1:1 Check-in", "Performance Review", "Career Discussion"],
            MeetingType.PRESENTATION: ["Demo Day", "Client Presentation", "Team Showcase"],
            MeetingType.TRAINING: ["Skills Workshop", "Training Session", "Knowledge Transfer"]
        }
        
        base_date = datetime.now(timezone.utc) - timedelta(days=30)
        user_ids = list(self.users.keys())
        
        for i in range(70):  # Generate 70 meetings
            meeting_type = random.choice(meeting_types)
            title = random.choice(titles[meeting_type])
            
            # Random participants (2-4 people)
            participants = random.sample(user_ids, random.randint(2, 4))
            organizer = random.choice(participants)
            
            # Random meeting time within last 30 days
            days_offset = random.randint(0, 30)
            hour = random.randint(9, 16)
            minute = random.choice([0, 15, 30, 45])
            
            start_time = base_date + timedelta(days=days_offset, hours=hour, minutes=minute)
            duration = random.choice([15, 30, 45, 60, 90])
            end_time = start_time + timedelta(minutes=duration)
            
            # Generate agenda
            agenda = self.meeting_templates.get(meeting_type.value, ["Meeting discussion"])
            
            # Random effectiveness score
            effectiveness = random.uniform(2.5, 5.0)
            
            meeting = Meeting(
                id=f"meeting_{i+1}",
                title=f"{title} #{i+1}",
                participants=participants,
                start_time=start_time,
                end_time=end_time,
                timezone="UTC",
                organizer=organizer,
                agenda=agenda,
                meeting_type=meeting_type.value,
                recurring=random.choice([True, False]),
                effectiveness_score=effectiveness,
                created_at=start_time - timedelta(days=random.randint(1, 5))
            )
            
            self.meetings[meeting.id] = meeting
    
    def find_optimal_slots(self, participants: List[str], duration: int, 
                          date_range: Tuple[datetime, datetime]) -> List[Dict]:
        """Find optimal meeting slots using AI-powered recommendations"""
        start_date, end_date = date_range
        optimal_slots = []
        
        # Get all participants' schedules
        participant_schedules = {}
        for participant_id in participants:
            if participant_id in self.users:
                participant_schedules[participant_id] = self.get_user_schedule(participant_id, start_date, end_date)
        
        # Generate potential time slots
        current_date = start_date
        while current_date <= end_date:
            # Check each hour of the day
            for hour in range(8, 18):  # 8 AM to 6 PM
                for minute in [0, 15, 30, 45]:
                    slot_start = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(minutes=duration)
                    
                    # Check if slot works for all participants
                    conflicts = self.check_slot_conflicts(participants, slot_start, slot_end)
                    if not conflicts:
                        # Calculate slot quality score
                        quality_score = self.calculate_slot_quality(participants, slot_start, slot_end)
                        
                        optimal_slots.append({
                            "start_time": slot_start.isoformat(),
                            "end_time": slot_end.isoformat(),
                            "quality_score": quality_score,
                            "timezone": "UTC",
                            "recommendation_reason": self.get_recommendation_reason(quality_score)
                        })
            
            current_date += timedelta(days=1)
        
        # Sort by quality score and return top 10
        optimal_slots.sort(key=lambda x: x["quality_score"], reverse=True)
        return optimal_slots[:10]
    
    def check_slot_conflicts(self, participants: List[str], start_time: datetime, end_time: datetime) -> List[str]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        for participant_id in participants:
            user_meetings = [m for m in self.meetings.values() if participant_id in m.participants]
            
            for meeting in user_meetings:
                if (start_time < meeting.end_time and end_time > meeting.start_time):
                    conflicts.append(f"Conflict with {meeting.title} for {participant_id}")
        
        return conflicts
    
    def calculate_slot_quality(self, participants: List[str], start_time: datetime, end_time: datetime) -> float:
        """Calculate quality score for a time slot"""
        score = 0.0
        
        for participant_id in participants:
            if participant_id in self.users:
                user = self.users[participant_id]
                
                # Check if time is within work hours
                day_name = start_time.strftime("%A").lower()
                if day_name in user.work_hours:
                    work_start, work_end = user.work_hours[day_name]
                    work_start_time = datetime.strptime(work_start, "%H:%M").time()
                    work_end_time = datetime.strptime(work_end, "%H:%M").time()
                    
                    if work_start_time <= start_time.time() <= work_end_time:
                        score += 2.0
                    else:
                        score -= 1.0
                
                # Check preferred meeting times
                if "preferred_times" in user.preferences:
                    preferred_hour = int(user.preferences["preferred_times"].split(":")[0])
                    if abs(start_time.hour - preferred_hour) <= 1:
                        score += 1.0
                
                # Avoid no-meeting times
                if "no_meeting_times" in user.preferences:
                    for no_meeting in user.preferences["no_meeting_times"]:
                        no_start, no_end = no_meeting.split("-")
                        no_start_time = datetime.strptime(no_start, "%H:%M").time()
                        no_end_time = datetime.strptime(no_end, "%H:%M").time()
                        
                        if no_start_time <= start_time.time() <= no_end_time:
                            score -= 2.0
        
        # Bonus for mid-week days
        if start_time.weekday() in [1, 2, 3]:  # Tuesday, Wednesday, Thursday
            score += 0.5
        
        # Bonus for mid-morning or early afternoon
        if start_time.hour in [10, 11, 14, 15]:
            score += 0.5
        
        return max(0, score / len(participants))
    
    def get_recommendation_reason(self, quality_score: float) -> str:
        """Get human-readable reason for recommendation"""
        if quality_score >= 2.0:
            return "Excellent time - within all participants' work hours and preferred times"
        elif quality_score >= 1.5:
            return "Good time - works well for most participants"
        elif quality_score >= 1.0:
            return "Acceptable time - some minor conflicts with preferences"
        else:
            return "Available time - may not be optimal for all participants"
    
    def get_user_schedule(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Meeting]:
        """Get user's schedule for a date range"""
        user_meetings = []
        for meeting in self.meetings.values():
            if user_id in meeting.participants:
                if start_date <= meeting.start_time <= end_date:
                    user_meetings.append(meeting)
        return user_meetings
    
    def detect_scheduling_conflicts(self, user_id: str, time_range: Tuple[datetime, datetime]) -> List[Dict]:
        """Detect scheduling conflicts for a user"""
        start_time, end_time = time_range
        conflicts = []
        
        user_meetings = self.get_user_schedule(user_id, start_time, end_time)
        
        # Sort meetings by start time
        user_meetings.sort(key=lambda m: m.start_time)
        
        for i in range(len(user_meetings) - 1):
            current_meeting = user_meetings[i]
            next_meeting = user_meetings[i + 1]
            
            # Check for overlapping meetings
            if current_meeting.end_time > next_meeting.start_time:
                conflicts.append({
                    "type": "overlap",
                    "meeting1": {
                        "id": current_meeting.id,
                        "title": current_meeting.title,
                        "start": current_meeting.start_time.isoformat(),
                        "end": current_meeting.end_time.isoformat()
                    },
                    "meeting2": {
                        "id": next_meeting.id,
                        "title": next_meeting.title,
                        "start": next_meeting.start_time.isoformat(),
                        "end": next_meeting.end_time.isoformat()
                    },
                    "severity": "high"
                })
            
            # Check for back-to-back meetings (no break)
            elif current_meeting.end_time == next_meeting.start_time:
                conflicts.append({
                    "type": "back_to_back",
                    "meeting1": {
                        "id": current_meeting.id,
                        "title": current_meeting.title,
                        "end": current_meeting.end_time.isoformat()
                    },
                    "meeting2": {
                        "id": next_meeting.id,
                        "title": next_meeting.title,
                        "start": next_meeting.start_time.isoformat()
                    },
                    "severity": "medium"
                })
        
        # Check for excessive daily meetings
        daily_meetings = defaultdict(list)
        for meeting in user_meetings:
            day = meeting.start_time.date()
            daily_meetings[day].append(meeting)
        
        if user_id in self.users:
            max_meetings = self.users[user_id].preferences.get("max_meetings_per_day", 8)
            for day, meetings in daily_meetings.items():
                if len(meetings) > max_meetings:
                    conflicts.append({
                        "type": "excessive_meetings",
                        "date": day.isoformat(),
                        "meeting_count": len(meetings),
                        "max_recommended": max_meetings,
                        "severity": "medium"
                    })
        
        return conflicts
    
    def analyze_meeting_patterns(self, user_id: str, period: str) -> Dict:
        """Analyze meeting patterns for a user"""
        # Define period
        end_date = datetime.now(timezone.utc)
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "quarter":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        user_meetings = self.get_user_schedule(user_id, start_date, end_date)
        
        if not user_meetings:
            return {"error": "No meetings found for the specified period"}
        
        # Calculate statistics
        total_meetings = len(user_meetings)
        total_duration = sum((m.end_time - m.start_time).total_seconds() / 3600 for m in user_meetings)
        avg_duration = total_duration / total_meetings if total_meetings > 0 else 0
        
        # Meeting types distribution
        type_distribution = defaultdict(int)
        for meeting in user_meetings:
            type_distribution[meeting.meeting_type] += 1
        
        # Daily meeting counts
        daily_counts = defaultdict(int)
        for meeting in user_meetings:
            day = meeting.start_time.strftime("%A")
            daily_counts[day] += 1
        
        # Meeting effectiveness analysis
        effectiveness_scores = [m.effectiveness_score for m in user_meetings if m.effectiveness_score]
        avg_effectiveness = statistics.mean(effectiveness_scores) if effectiveness_scores else 0
        
        # Peak meeting hours
        hourly_counts = defaultdict(int)
        for meeting in user_meetings:
            hour = meeting.start_time.hour
            hourly_counts[hour] += 1
        
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else 0
        
        return {
            "period": period,
            "total_meetings": total_meetings,
            "total_hours": round(total_duration, 2),
            "average_duration_minutes": round(avg_duration * 60, 2),
            "effectiveness_score": round(avg_effectiveness, 2),
            "meeting_types": dict(type_distribution),
            "daily_distribution": dict(daily_counts),
            "peak_meeting_hour": peak_hour,
            "recommendations": self.generate_pattern_recommendations(user_meetings, user_id)
        }
    
    def generate_pattern_recommendations(self, meetings: List[Meeting], user_id: str) -> List[str]:
        """Generate recommendations based on meeting patterns"""
        recommendations = []
        
        if not meetings:
            return recommendations
        
        # Check for excessive meetings
        daily_meetings = defaultdict(list)
        for meeting in meetings:
            day = meeting.start_time.date()
            daily_meetings[day].append(meeting)
        
        avg_daily_meetings = sum(len(meetings) for meetings in daily_meetings.values()) / len(daily_meetings)
        
        if avg_daily_meetings > 6:
            recommendations.append("Consider reducing daily meeting load - current average is high")
        
        # Check meeting effectiveness
        effectiveness_scores = [m.effectiveness_score for m in meetings if m.effectiveness_score]
        if effectiveness_scores:
            avg_effectiveness = statistics.mean(effectiveness_scores)
            if avg_effectiveness < 3.0:
                recommendations.append("Focus on improving meeting effectiveness - current score is below average")
        
        # Check for long meetings
        long_meetings = [m for m in meetings if (m.end_time - m.start_time).total_seconds() / 3600 > 1.5]
        if len(long_meetings) > len(meetings) * 0.3:
            recommendations.append("Consider breaking down long meetings into shorter, focused sessions")
        
        # Check for back-to-back meetings
        sorted_meetings = sorted(meetings, key=lambda m: m.start_time)
        back_to_back_count = 0
        for i in range(len(sorted_meetings) - 1):
            if sorted_meetings[i].end_time >= sorted_meetings[i + 1].start_time:
                back_to_back_count += 1
        
        if back_to_back_count > len(meetings) * 0.2:
            recommendations.append("Schedule buffer time between meetings to avoid fatigue")
        
        return recommendations
    
    def generate_agenda_suggestions(self, meeting_topic: str, participants: List[str]) -> List[str]:
        """Generate smart agenda suggestions"""
        # Determine meeting type based on topic
        topic_lower = meeting_topic.lower()
        
        if any(word in topic_lower for word in ["standup", "daily", "sync"]):
            meeting_type = "standup"
        elif any(word in topic_lower for word in ["review", "retrospective"]):
            meeting_type = "review"
        elif any(word in topic_lower for word in ["planning", "plan"]):
            meeting_type = "planning"
        elif any(word in topic_lower for word in ["brainstorm", "ideation", "creative"]):
            meeting_type = "brainstorm"
        elif len(participants) == 2:
            meeting_type = "one_on_one"
        else:
            meeting_type = "review"  # Default
        
        # Get base template
        base_agenda = self.meeting_templates.get(meeting_type, ["Meeting discussion"])
        
        # Customize based on participants
        if len(participants) > 5:
            base_agenda.insert(0, "Introductions and attendance")
            base_agenda.append("Large group coordination")
        
        # Add topic-specific items
        if "project" in topic_lower:
            base_agenda.append("Project timeline review")
        if "budget" in topic_lower:
            base_agenda.append("Budget discussion")
        if "launch" in topic_lower:
            base_agenda.append("Launch preparation checklist")
        
        # Always end with action items
        if "Action items and next steps" not in base_agenda:
            base_agenda.append("Action items and next steps")
        
        return base_agenda
    
    def calculate_workload_balance(self, team_members: List[str]) -> Dict:
        """Calculate meeting workload balance across team members"""
        workload_data = {}
        
        # Calculate last 2 weeks of meetings
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=14)
        
        for member_id in team_members:
            if member_id in self.users:
                user_meetings = self.get_user_schedule(member_id, start_date, end_date)
                
                total_hours = sum((m.end_time - m.start_time).total_seconds() / 3600 for m in user_meetings)
                meeting_count = len(user_meetings)
                
                # Calculate daily averages
                daily_hours = total_hours / 14
                daily_meetings = meeting_count / 14
                
                workload_data[member_id] = {
                    "user_name": self.users[member_id].name,
                    "total_meeting_hours": round(total_hours, 2),
                    "total_meetings": meeting_count,
                    "daily_avg_hours": round(daily_hours, 2),
                    "daily_avg_meetings": round(daily_meetings, 2),
                    "workload_level": self.categorize_workload(daily_hours, daily_meetings)
                }
        
        # Calculate team statistics
        if workload_data:
            total_hours = [data["total_meeting_hours"] for data in workload_data.values()]
            avg_team_hours = statistics.mean(total_hours)
            workload_variance = statistics.variance(total_hours) if len(total_hours) > 1 else 0
            
            return {
                "team_members": workload_data,
                "team_average_hours": round(avg_team_hours, 2),
                "workload_variance": round(workload_variance, 2),
                "balance_score": self.calculate_balance_score(workload_variance),
                "recommendations": self.generate_workload_recommendations(workload_data)
            }
        
        return {"error": "No valid team members found"}
    
    def categorize_workload(self, daily_hours: float, daily_meetings: float) -> str:
        """Categorize workload level"""
        if daily_hours > 4 or daily_meetings > 6:
            return "High"
        elif daily_hours > 2 or daily_meetings > 4:
            return "Medium"
        else:
            return "Low"
    
    def calculate_balance_score(self, variance: float) -> float:
        """Calculate balance score (0-10, higher is better)"""
        # Lower variance = better balance
        if variance == 0:
            return 10.0
        elif variance < 1:
            return 8.0
        elif variance < 4:
            return 6.0
        elif variance < 9:
            return 4.0
        else:
            return 2.0
    
    def generate_workload_recommendations(self, workload_data: Dict) -> List[str]:
        """Generate workload balancing recommendations"""
        recommendations = []
        
        high_workload_members = [
            member_id for member_id, data in workload_data.items() 
            if data["workload_level"] == "High"
        ]
        
        low_workload_members = [
            member_id for member_id, data in workload_data.items() 
            if data["workload_level"] == "Low"
        ]
        
        if high_workload_members:
            recommendations.append(f"Consider redistributing meetings from high-workload members: {', '.join([workload_data[m]['user_name'] for m in high_workload_members])}")
        
        if low_workload_members and high_workload_members:
            recommendations.append("Balance workload by involving low-workload members in more meetings")
        
        # Check for extreme imbalances
        hours_list = [data["total_meeting_hours"] for data in workload_data.values()]
        if max(hours_list) - min(hours_list) > 10:
            recommendations.append("Significant workload imbalance detected - consider restructuring meeting assignments")
        
        return recommendations
    
    def score_meeting_effectiveness(self, meeting_id: str) -> Dict:
        """Score meeting effectiveness and provide improvement suggestions"""
        if meeting_id not in self.meetings:
            return {"error": "Meeting not found"}
        
        meeting = self.meetings[meeting_id]
        
        # Base effectiveness score (if available)
        base_score = meeting.effectiveness_score or 3.0
        
        # Calculate additional factors
        duration_minutes = (meeting.end_time - meeting.start_time).total_seconds() / 60
        participant_count = len(meeting.participants)
        
        # Duration score (sweet spot is 30-45 minutes)
        if 30 <= duration_minutes <= 45:
            duration_score = 1.0
        elif 15 <= duration_minutes <= 60:
            duration_score = 0.8
        elif duration_minutes > 90:
            duration_score = 0.3
        else:
            duration_score = 0.6
        
        # Participant count score (3-6 people is optimal)
        if 3 <= participant_count <= 6:
            participant_score = 1.0
        elif participant_count <= 8:
            participant_score = 0.8
        else:
            participant_score = 0.5
        
        # Agenda score (having agenda improves effectiveness)
        agenda_score = 1.0 if meeting.agenda and len(meeting.agenda) > 2 else 0.7
        
        # Calculate final score
        final_score = base_score * duration_score * participant_score * agenda_score
        final_score = min(5.0, max(1.0, final_score))
        
        # Generate improvement suggestions
        improvements = []
        
        if duration_minutes > 60:
            improvements.append("Consider shortening meeting duration or breaking into multiple sessions")
        
        if participant_count > 8:
            improvements.append("Reduce number of participants to key stakeholders only")
        
        if not meeting.agenda or len(meeting.agenda) < 3:
            improvements.append("Prepare detailed agenda with clear objectives")
        
        if final_score < 3.0:
            improvements.append("Schedule follow-up to address unresolved topics")
        
        if meeting.meeting_type == "standup" and duration_minutes > 30:
            improvements.append("Keep standup meetings under 30 minutes")
        
        return {
            "meeting_id": meeting_id,
            "meeting_title": meeting.title,
            "effectiveness_score": round(final_score, 2),
            "score_breakdown": {
                "base_score": base_score,
                "duration_factor": duration_score,
                "participant_factor": participant_score,
                "agenda_factor": agenda_score
            },
            "improvement_suggestions": improvements,
            "meeting_details": {
                "duration_minutes": int(duration_minutes),
                "participant_count": participant_count,
                "has_agenda": bool(meeting.agenda),
                "meeting_type": meeting.meeting_type
            }
        }
    
    def optimize_meeting_schedule(self, user_id: str) -> Dict:
        """Provide schedule optimization recommendations"""
        if user_id not in self.users:
            return {"error": "User not found"}
        
        user = self.users[user_id]
        
        # Get recent meetings (last 2 weeks)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=14)
        user_meetings = self.get_user_schedule(user_id, start_date, end_date)
        
        optimizations = []
        
        # Check for meeting-free focus blocks
        focus_blocks = self.identify_focus_blocks(user_meetings)
        if len(focus_blocks) < 3:
            optimizations.append({
                "type": "focus_time",
                "priority": "high",
                "recommendation": "Schedule 2-3 blocks of uninterrupted focus time daily",
                "impact": "Increases productivity by 25-40%"
            })
        
        # Check for meeting clustering
        scattered_meetings = self.check_meeting_clustering(user_meetings)
        if scattered_meetings:
            optimizations.append({
                "type": "clustering",
                "priority": "medium",
                "recommendation": "Group meetings together to create longer focus periods",
                "impact": "Reduces context switching overhead"
            })
        
        # Check for optimal meeting times
        suboptimal_times = self.identify_suboptimal_times(user_meetings, user)
        if suboptimal_times:
            optimizations.append({
                "type": "timing",
                "priority": "medium",
                "recommendation": "Move meetings to more optimal times based on your preferences",
                "impact": "Improves meeting engagement and effectiveness"
            })
        
        # Check for recurring meeting optimization
        recurring_meetings = [m for m in user_meetings if m.recurring]
        if len(recurring_meetings) > 5:
            optimizations.append({
                "type": "recurring",
                "priority": "low",
                "recommendation": "Review necessity of recurring meetings - cancel or reduce frequency",
                "impact": "Frees up 2-5 hours per week"
            })
        
        return {
            "user_id": user_id,
            "user_name": user.name,
            "optimization_score": self.calculate_optimization_score(optimizations),
            "recommendations": optimizations,
            "current_stats": {
                "meetings_per_week": len(user_meetings),
                "hours_per_week": sum((m.end_time - m.start_time).total_seconds() / 3600 for m in user_meetings),
                "focus_blocks_per_week": len(focus_blocks)
            }
        }
    
    def identify_focus_blocks(self, meetings: List[Meeting]) -> List[Dict]:
        """Identify existing focus blocks (2+ hour gaps between meetings)"""
        focus_blocks = []
        
        # Group meetings by day
        daily_meetings = defaultdict(list)
        for meeting in meetings:
            day = meeting.start_time.date()
            daily_meetings[day].append(meeting)
        
        for day, day_meetings in daily_meetings.items():
            day_meetings.sort(key=lambda m: m.start_time)
            
            # Check gaps between meetings
            for i in range(len(day_meetings) - 1):
                gap_start = day_meetings[i].end_time
                gap_end = day_meetings[i + 1].start_time
                gap_duration = (gap_end - gap_start).total_seconds() / 3600
                
                if gap_duration >= 2:
                    focus_blocks.append({
                        "date": day.isoformat(),
                        "start": gap_start.isoformat(),
                        "end": gap_end.isoformat(),
                        "duration_hours": gap_duration
                    })
        
        return focus_blocks
    
    def check_meeting_clustering(self, meetings: List[Meeting]) -> bool:
        """Check if meetings are scattered throughout the day"""
        # Group meetings by day
        daily_meetings = defaultdict(list)
        for meeting in meetings:
            day = meeting.start_time.date()
            daily_meetings[day].append(meeting)
        
        scattered_days = 0
        for day, day_meetings in daily_meetings.items():
            if len(day_meetings) < 2:
                continue
                
            day_meetings.sort(key=lambda m: m.start_time)
            
            # Check if meetings span more than 6 hours
            first_meeting = day_meetings[0]
            last_meeting = day_meetings[-1]
            span_hours = (last_meeting.end_time - first_meeting.start_time).total_seconds() / 3600
            
            if span_hours > 6 and len(day_meetings) > 2:
                scattered_days += 1
        
        return scattered_days > len(daily_meetings) * 0.3
    
    def identify_suboptimal_times(self, meetings: List[Meeting], user: User) -> List[str]:
        """Identify meetings at suboptimal times"""
        suboptimal = []
        
        for meeting in meetings:
            # Check if outside preferred work hours
            day_name = meeting.start_time.strftime("%A").lower()
            if day_name in user.work_hours:
                work_start, work_end = user.work_hours[day_name]
                work_start_time = datetime.strptime(work_start, "%H:%M").time()
                work_end_time = datetime.strptime(work_end, "%H:%M").time()
                
                if not (work_start_time <= meeting.start_time.time() <= work_end_time):
                    suboptimal.append(meeting.title)
        
        return suboptimal
    
    def calculate_optimization_score(self, optimizations: List[Dict]) -> int:
        """Calculate optimization score (0-100)"""
        base_score = 100
        
        for opt in optimizations:
            if opt["priority"] == "high":
                base_score -= 25
            elif opt["priority"] == "medium":
                base_score -= 15
            elif opt["priority"] == "low":
                base_score -= 10
        
        return max(0, base_score)
    
    def create_meeting(self, title: str, participants: List[str], duration: int, 
                      start_time: datetime, preferences: Dict = None) -> Dict:
        """Create a new meeting"""
        meeting_id = f"meeting_{len(self.meetings) + 1}"
        
        # Check for conflicts
        conflicts = []
        for participant in participants:
            participant_conflicts = self.check_slot_conflicts(
                [participant], start_time, start_time + timedelta(minutes=duration)
            )
            conflicts.extend(participant_conflicts)
        
        if conflicts:
            return {
                "success": False,
                "meeting_id": None,
                "conflicts": conflicts,
                "message": "Meeting conflicts detected"
            }
        
        # Create meeting
        end_time = start_time + timedelta(minutes=duration)
        organizer = participants[0] if participants else "unknown"
        
        meeting = Meeting(
            id=meeting_id,
            title=title,
            participants=participants,
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            organizer=organizer,
            agenda=self.generate_agenda_suggestions(title, participants),
            meeting_type="general",
            created_at=datetime.now(timezone.utc)
        )
        
        self.meetings[meeting_id] = meeting
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "meeting": asdict(meeting),
            "suggested_agenda": meeting.agenda,
            "message": "Meeting created successfully"
        }

# Initialize the MCP server
app = Server("smart-meeting-assistant")
assistant = SmartMeetingAssistant()

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="meetings://calendar",
            name="Meeting Calendar",
            description="Access to meeting calendar data",
            mimeType="application/json"
        ),
        Resource(
            uri="meetings://users",
            name="User Directory",
            description="Access to user information and preferences",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource data"""
    if uri == "meetings://calendar":
        return json.dumps([asdict(meeting) for meeting in assistant.meetings.values()], default=str)
    elif uri == "meetings://users":
        return json.dumps([asdict(user) for user in assistant.users.values()], default=str)
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="create_meeting",
            description="Schedule a new meeting with conflict detection",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Meeting title"},
                    "participants": {"type": "array", "items": {"type": "string"}, "description": "List of participant IDs"},
                    "duration": {"type": "integer", "description": "Meeting duration in minutes"},
                    "start_time": {"type": "string", "format": "date-time", "description": "Meeting start time"},
                    "preferences": {"type": "object", "description": "Meeting preferences"}
                },
                "required": ["title", "participants", "duration", "start_time"]
            }
        ),
        Tool(
            name="find_optimal_slots",
            description="Find optimal meeting time slots using AI recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "participants": {"type": "array", "items": {"type": "string"}, "description": "List of participant IDs"},
                    "duration": {"type": "integer", "description": "Meeting duration in minutes"},
                    "start_date": {"type": "string", "format": "date", "description": "Search start date"},
                    "end_date": {"type": "string", "format": "date", "description": "Search end date"}
                },
                "required": ["participants", "duration", "start_date", "end_date"]
            }
        ),
        Tool(
            name="detect_scheduling_conflicts",
            description="Detect scheduling conflicts for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to check"},
                    "start_time": {"type": "string", "format": "date-time", "description": "Start time for conflict check"},
                    "end_time": {"type": "string", "format": "date-time", "description": "End time for conflict check"}
                },
                "required": ["user_id", "start_time", "end_time"]
            }
        ),
        Tool(
            name="analyze_meeting_patterns",
            description="Analyze meeting patterns and behavior",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to analyze"},
                    "period": {"type": "string", "enum": ["week", "month", "quarter"], "description": "Analysis period"}
                },
                "required": ["user_id", "period"]
            }
        ),
        Tool(
            name="generate_agenda_suggestions",
            description="Generate smart agenda suggestions for meetings",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_topic": {"type": "string", "description": "Meeting topic or title"},
                    "participants": {"type": "array", "items": {"type": "string"}, "description": "List of participant IDs"}
                },
                "required": ["meeting_topic", "participants"]
            }
        ),
        Tool(
            name="calculate_workload_balance",
            description="Calculate meeting workload balance across team members",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_members": {"type": "array", "items": {"type": "string"}, "description": "List of team member IDs"}
                },
                "required": ["team_members"]
            }
        ),
        Tool(
            name="score_meeting_effectiveness",
            description="Score meeting effectiveness and provide improvement suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "string", "description": "Meeting ID to score"}
                },
                "required": ["meeting_id"]
            }
        ),
        Tool(
            name="optimize_meeting_schedule",
            description="Provide schedule optimization recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to optimize"}
                },
                "required": ["user_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "create_meeting":
            start_time = datetime.fromisoformat(arguments["start_time"].replace("Z", "+00:00"))
            result = assistant.create_meeting(
                arguments["title"],
                arguments["participants"],
                arguments["duration"],
                start_time,
                arguments.get("preferences")
            )
            
        elif name == "find_optimal_slots":
            start_date = datetime.fromisoformat(arguments["start_date"] + "T00:00:00+00:00")
            end_date = datetime.fromisoformat(arguments["end_date"] + "T23:59:59+00:00")
            result = assistant.find_optimal_slots(
                arguments["participants"],
                arguments["duration"],
                (start_date, end_date)
            )
            
        elif name == "detect_scheduling_conflicts":
            start_time = datetime.fromisoformat(arguments["start_time"].replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(arguments["end_time"].replace("Z", "+00:00"))
            result = assistant.detect_scheduling_conflicts(
                arguments["user_id"],
                (start_time, end_time)
            )
            
        elif name == "analyze_meeting_patterns":
            result = assistant.analyze_meeting_patterns(
                arguments["user_id"],
                arguments["period"]
            )
            
        elif name == "generate_agenda_suggestions":
            result = assistant.generate_agenda_suggestions(
                arguments["meeting_topic"],
                arguments["participants"]
            )
            
        elif name == "calculate_workload_balance":
            result = assistant.calculate_workload_balance(
                arguments["team_members"]
            )
            
        elif name == "score_meeting_effectiveness":
            result = assistant.score_meeting_effectiveness(
                arguments["meeting_id"]
            )
            
        elif name == "optimize_meeting_schedule":
            result = assistant.optimize_meeting_schedule(
                arguments["user_id"]
            )
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]

async def main():
    """Main function to run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, InitializationOptions(
            server_name="smart-meeting-assistant",
            server_version="1.0.0",
            capabilities=app.get_capabilities(
                notification=True,
                experimental={}
            )
        ))

if __name__ == "__main__":
    asyncio.run(main())
