#!/usr/bin/env python3
"""Update Google Forms to be bilingual (Chinese + English)"""
import json, os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE=os.path.expanduser("~/.hermes/google_token.json")

with open(TOKEN_FILE) as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data, [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

forms = build("forms", "v1", credentials=creds)

# ── Form 1: Chef Resume (厨师简历) ──
CHEF_FORM_ID = "1u9NQEu2FHw8nMe6FdNZBobpAe4DorJZtwONdeqxI3d4"

chef_questions = [
    # Q1: Name
    {
        "updateItem": {
            "item": {
                "title": "你的名字 / Your Name *",
                "description": "（中文或英文 / Chinese or English）",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 0},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q2: Specialty
    {
        "updateItem": {
            "item": {
                "title": "擅长菜系 / Culinary Specialty *",
                "description": "如：中餐·粤菜、西餐·烘焙、马来餐 / e.g. Chinese Cuisine, Western, Pastry",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 1},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q3: Experience
    {
        "updateItem": {
            "item": {
                "title": "从业经验 / Years of Experience *",
                "description": "",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 2},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q4: Location
    {
        "updateItem": {
            "item": {
                "title": "所在地区 / Location *",
                "description": "如：新山 Johor Bahru、Mount Austin、Skudai",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 3},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q5: Salary
    {
        "updateItem": {
            "item": {
                "title": "期望薪资 / Expected Salary",
                "description": "如：RM 4000 - RM 5500",
                "questionItem": {
                    "question": {
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 4},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q6: Availability
    {
        "updateItem": {
            "item": {
                "title": "可到岗时间 / Availability",
                "description": "随时 / 两周内 / 一个月内 / Immediate / 2 weeks / 1 month",
                "questionItem": {
                    "question": {
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 5},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q7: Phone
    {
        "updateItem": {
            "item": {
                "title": "联系电话 / Phone / WhatsApp *",
                "description": "雇主会通过这个号码联系你 / Employers will contact you via this number",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 6},
            "updateMask": "title,description,questionItem"
        }
    },
    # Q8: Intro
    {
        "updateItem": {
            "item": {
                "title": "自我介绍 / Self Introduction",
                "description": "简述工作经历和经验 / Briefly describe your work experience",
                "questionItem": {
                    "question": {
                        "textQuestion": {"paragraph": True}
                    }
                }
            },
            "location": {"index": 7},
            "updateMask": "title,description,questionItem"
        }
    },
]

forms.forms().batchUpdate(formId=CHEF_FORM_ID, body={"requests": chef_questions}).execute()
print(f"✅ 厨师简历表单已更新为中英文")
print(f"   https://docs.google.com/forms/d/e/1FAIpQLScJVkyYraKTstINyqyZDlA_3wJNCVj6ohHOMCs4Gtv6nChRBw/viewform")

# ── Form 2: Supplier Submission (供应商提交) ──
# Find the supplier form by searching Drive
drive = build("drive", "v3", credentials=creds)
results = drive.files().list(
    q="name contains '供应商' and mimeType='application/vnd.google-apps.form'",
    fields="files(id, name)"
).execute()

if results.get("files"):
    supplier_form_id = results["files"][0]["id"]
    print(f"找到供应商表单: {supplier_form_id}")
else:
    # Create it
    form = {
        "info": {
            "title": "jbkitchen — 供应商提交 / Supplier Submission",
            "document_title": "jbkitchen 供应商提交"
        }
    }
    result = forms.forms().create(body=form).execute()
    supplier_form_id = result["formId"]
    print(f"创建供应商表单: {supplier_form_id}")

supplier_questions = [
    {
        "updateItem": {
            "item": {
                "title": "商家名称 / Business Name *",
                "description": "公司或品牌名称 / Company or brand name",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 0},
            "updateMask": "title,description,questionItem"
        }
    },
    {
        "updateItem": {
            "item": {
                "title": "联系人 / Contact Person *",
                "description": "",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 1},
            "updateMask": "title,description,questionItem"
        }
    },
    {
        "updateItem": {
            "item": {
                "title": "联系电话 / Phone *",
                "description": "",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 2},
            "updateMask": "title,description,questionItem"
        }
    },
    {
        "updateItem": {
            "item": {
                "title": "地址 / Address",
                "description": "如：新山 Johor Bahru、Mount Austin",
                "questionItem": {
                    "question": {
                        "textQuestion": {}
                    }
                }
            },
            "location": {"index": 3},
            "updateMask": "title,description,questionItem"
        }
    },
    {
        "updateItem": {
            "item": {
                "title": "主要产品 / Main Products *",
                "description": "如：冷冻鸡、海鲜、蔬菜、调味料 / e.g. Frozen chicken, seafood, vegetables, sauces",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {"paragraph": True}
                    }
                }
            },
            "location": {"index": 4},
            "updateMask": "title,description,questionItem"
        }
    },
    {
        "updateItem": {
            "item": {
                "title": "备注 / Notes",
                "description": "其他你想告诉我们的信息 / Anything else you'd like us to know",
                "questionItem": {
                    "question": {
                        "textQuestion": {"paragraph": True}
                    }
                }
            },
            "location": {"index": 5},
            "updateMask": "title,description,questionItem"
        }
    },
]

forms.forms().batchUpdate(formId=supplier_form_id, body={"requests": supplier_questions}).execute()

# Get the responder URL
form_info = forms.forms().get(formId=supplier_form_id).execute()
supplier_url = form_info.get("responderUri", "")
print(f"✅ 供应商提交表单已更新为中英文")
print(f"   URL: {supplier_url}")
print(f"   Edit: https://docs.google.com/forms/d/{supplier_form_id}/edit")
