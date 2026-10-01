import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Issue, CriticalIssue, LowPriorityIssue, Reporter

# issues/views.py -> issues/ -> project root (where manage.py lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTERS_FILE = os.path.join(BASE_DIR, "reporters.json")
ISSUES_FILE = os.path.join(BASE_DIR, "issues.json")


def read_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def error(message, status):
    return JsonResponse({"error": message}, status=status)


# ---------------------------------------------------------------- reporters

@csrf_exempt
def reporters_view(request):
    if request.method == "POST":
        return create_reporter(request)
    if request.method == "GET":
        return get_reporters(request)
    return error("Only GET and POST methods are allowed", 405)


def create_reporter(request):
    try:
        data = json.loads(request.body)
        reporter = Reporter(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            team=data["team"],
        )
        reporter.validate()

        reporters = read_json(REPORTERS_FILE)
        if any(r["id"] == reporter.id for r in reporters):
            return error("Reporter with this id already exists", 400)

        reporters.append(reporter.to_dict())
        write_json(REPORTERS_FILE, reporters)
        return JsonResponse(reporter.to_dict(), status=201)

    # JSONDecodeError is a subclass of ValueError, so it must come first
    except json.JSONDecodeError:
        return error("Invalid JSON", 400)
    except ValueError as e:
        return error(str(e), 400)
    except KeyError as e:
        return error(f"Missing field: {e.args[0]}", 400)


def get_reporters(request):
    reporters = read_json(REPORTERS_FILE)
    reporter_id = request.GET.get("id")

    if reporter_id:
        try:
            reporter_id = int(reporter_id)
        except ValueError:
            return error("Invalid id", 400)

        for reporter in reporters:
            if reporter["id"] == reporter_id:
                return JsonResponse(reporter, status=200)
        return error("Reporter not found", 404)

    return JsonResponse(reporters, safe=False, status=200)


# ------------------------------------------------------------------ issues

@csrf_exempt
def issues_view(request):
    if request.method == "POST":
        return create_issue(request)
    if request.method == "GET":
        return get_issues(request)
    return error("Only GET and POST methods are allowed", 405)


def create_issue(request):
    try:
        data = json.loads(request.body)

        fields = dict(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=data["status"],
            priority=data["priority"],
            reporter_id=data["reporter_id"],
        )

        if data["priority"] == "critical":
            issue = CriticalIssue(**fields)
        elif data["priority"] == "low":
            issue = LowPriorityIssue(**fields)
        else:
            issue = Issue(**fields)

        issue.validate()

        # the reporter must exist, and the issue id must be unique
        if not any(r["id"] == issue.reporter_id for r in read_json(REPORTERS_FILE)):
            return error("Reporter not found", 400)

        issues = read_json(ISSUES_FILE)
        if any(i["id"] == issue.id for i in issues):
            return error("Issue with this id already exists", 400)

        issues.append(issue.to_dict())
        write_json(ISSUES_FILE, issues)

        response_data = issue.to_dict()
        response_data["message"] = issue.describe()
        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return error("Invalid JSON", 400)
    except ValueError as e:
        return error(str(e), 400)
    except KeyError as e:
        return error(f"Missing field: {e.args[0]}", 400)


def get_issues(request):
    issues = read_json(ISSUES_FILE)
    issue_id = request.GET.get("id")
    status = request.GET.get("status")

    if issue_id:
        try:
            issue_id = int(issue_id)
        except ValueError:
            return error("Invalid id", 400)

        for issue in issues:
            if issue["id"] == issue_id:
                return JsonResponse(issue, status=200)
        return error("Issue not found", 404)

    if status:
        issues = [i for i in issues if i["status"] == status]

    return JsonResponse(issues, safe=False, status=200)