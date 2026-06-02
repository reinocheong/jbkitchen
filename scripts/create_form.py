#!/usr/bin/env python3
"""Create Google Form for chef resume submission"""
import json, os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")

with open(TOKEN_FILE) as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data, [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

forms = build("forms", "v1", credentials=creds)

# Create form
form = {
    "info": {
        "title": "jbkitchen — 厨师简历提交",
        "document_title": "jbkitchen 厨师简历"
    }
}
result = forms.forms().create(body=form).execute()
form_id = result["formId"]
form_url = result["responderUri"]
print(f"Form ID: {form_id}")
print(f"Form URL: {form_url}")

# Add questions
questions = [
    ("你的名字", "（中文或英文）", False, False),
    ("擅长菜系/领域", "如：中餐·粤菜、西餐·烘焙、马来餐（可多选）", False, False),
    ("从业经验（年）", "", False, False),
    ("所在地区", "如：新山 Johor Bahru、Mount Austin、Skudai", False, False),
    ("期望薪资", "如：RM 4000 - RM 5500", True, False),
    ("可到岗时间", "如：随时、两周内、一个月内", True, False),
    ("联系电话 / WhatsApp", "雇主会通过这个号码联系你", False, False),
    ("自我介绍 / 工作经历简述", "", True, True),
]

batch = {"requests": []}
for i, (title, desc, optional, paragraph) in enumerate(questions):
    item = {
        "title": title,
        "questionItem": {
            "question": {
                "required": not optional,
                "textQuestion": {"paragraph": paragraph} if paragraph else {}
            }
        }
    }
    if desc:
        item["description"] = desc
    batch["requests"].append({
        "createItem": {
            "item": item,
            "location": {"index": i}
        }
    })

forms.forms().batchUpdate(formId=form_id, body=batch).execute()

# Also link to Google Sheet for responses
drive = build("drive", "v3", credentials=creds)

print(f"\n✅ 表单创建成功!")
print(f"URL: {form_url}")
print(f"Edit: https://docs.google.com/forms/d/{form_id}/edit")
print(f"Responses Sheet: will be auto-created by Google Forms")
