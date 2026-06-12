from enum import StrEnum


class WorkoutPages(StrEnum):
    CREATE_EXERCISE = "workout/create_exercise.html"
    CREATE_PLAN = "workout/create_plan.html"
    DAY = "workout/day.html"
    EXERCISE = "workout/exercise.html"
    EXERCISES = "workout/exercises.html"
    PLAN = "workout/plan.html"
    PLANS = "workout/list_plans.html"

class UserPages(StrEnum):
    LOGIN = "users/login.html"
    PROFILE = "users/profile.html"
    SIGNUP = "users/signup.html"
