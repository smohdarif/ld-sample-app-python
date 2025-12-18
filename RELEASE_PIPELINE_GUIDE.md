# LaunchDarkly Release Pipeline Guide

A complete step-by-step guide to creating feature flags and release pipelines using the LaunchDarkly API. This guide follows the actual workflow used to create the **ZipHQ** flag and release pipeline.

## Prerequisites

- LaunchDarkly API Access Token (starts with `api-`)
- Project key (e.g., `arif-skyhigh-releasedemo`)
- Python 3.x installed

## Table of Contents

1. [Setup MCP Server for Cursor](#step-1-setup-mcp-server-for-cursor)
2. [List Existing Release Pipelines](#step-2-list-existing-release-pipelines)
3. [Create a Feature Flag](#step-3-create-a-feature-flag)
4. [Create a New Release Pipeline](#step-4-create-a-new-release-pipeline)
5. [Add Flag to Release Pipeline](#step-5-add-flag-to-release-pipeline)
6. [Start Phase 1 (Dev)](#step-6-start-phase-1-dev)
7. [Integrate Flag in Your Application](#step-7-integrate-flag-in-your-application)
8. [Test the Flag](#step-8-test-the-flag)
9. [Get Release Status](#step-9-get-release-status)
10. [Complete Phase and Progress to QA](#step-10-complete-phase-and-progress-to-qa)

---

## Overview: Release Pipeline Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Phase 1      │    │    Phase 2      │    │    Phase 3      │    │    Phase 4      │
│      Dev        │ →  │       QA        │ →  │   Integration   │ →  │   Production    │
│                 │    │                 │    │                 │    │                 │
│  Flag ON in Dev │    │  Flag ON in QA  │    │  Flag ON in Int │    │  Flag ON in Prod│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Step 1: Setup MCP Server for Cursor

The LaunchDarkly MCP Server enables AI assistants to interact with LaunchDarkly APIs directly from Cursor IDE.

### 1.1 Create Configuration File

Create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "LaunchDarkly": {
      "command": "npx",
      "args": [
        "-y",
        "--package",
        "@launchdarkly/mcp-server",
        "--",
        "mcp",
        "start",
        "--api-key",
        "YOUR_API_KEY_HERE"
      ]
    }
  }
}
```

### 1.2 Security Configuration

Add `.cursor/` to your `.gitignore` to prevent committing API keys:

```gitignore
# Cursor IDE config (contains API keys)
.cursor/
```

### 1.3 Activate the MCP Server

1. Restart Cursor IDE (`Cmd+Shift+P` → "Reload Window")
2. Go to **Cursor Settings → Features → MCP Servers**
3. Verify "LaunchDarkly" shows as connected

> ⚠️ **Note**: If you see "No server info found" error, ensure you're using `--api-key` (not `--access-token`) in the configuration.

---

## Step 2: List Existing Release Pipelines

Before creating a new pipeline, check what already exists in your project.

### Request

```
GET https://app.launchdarkly.com/api/v2/projects/{projectKey}/release-pipelines
```

### Headers

```
Authorization: <YOUR_API_KEY>
Content-Type: application/json
LD-API-Version: beta
```

> ⚠️ **Important**: The `LD-API-Version: beta` header is required for all release pipeline APIs.

### Python Code

```python
import urllib.request
import json

url = 'https://app.launchdarkly.com/api/v2/projects/arif-skyhigh-releasedemo/release-pipelines'

req = urllib.request.Request(url)
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    print(json.dumps(data, indent=2))
```

### Response Example

```json
{
  "items": [
    {
      "createdAt": "2025-09-16T22:01:04.602697Z",
      "description": "",
      "key": "release-pipeline-1",
      "name": "Release pipeline 1",
      "phases": [
        {
          "id": "f4a85edb-3871-4a01-bf63-a43fe80cd4d6",
          "name": "Dev",
          "audiences": [
            {
              "environment": {
                "key": "dev",
                "name": "Dev",
                "color": "00da7b"
              },
              "name": "Dev",
              "configuration": {
                "releaseStrategy": "immediate-rollout",
                "requireApproval": false
              }
            }
          ]
        },
        {
          "id": "67e742ae-e84d-4d97-ba78-163c438a2380",
          "name": "QA",
          "audiences": [...]
        },
        {
          "id": "e3e1d094-4637-493c-bcc4-b17c9da9e54d",
          "name": "Integration",
          "audiences": [...]
        },
        {
          "id": "563cd0c4-f4c0-482b-9cd4-a7b79cb2e375",
          "name": "Production",
          "audiences": [...]
        }
      ],
      "isProjectDefault": true
    }
  ],
  "totalCount": 1
}
```

---

## Step 3: Create a Feature Flag

Create a new boolean feature flag that will be managed through the release pipeline.

### Request

```
POST https://app.launchdarkly.com/api/v2/flags/{projectKey}
```

### Headers

```
Authorization: <YOUR_API_KEY>
Content-Type: application/json
```

### Request Body

```json
{
  "name": "ZipHQ",
  "key": "ziphq",
  "description": "ZipHQ feature flag for release pipeline demo",
  "temporary": true,
  "tags": ["demo", "ziphq"],
  "clientSideAvailability": {
    "usingEnvironmentId": true,
    "usingMobileKey": false
  },
  "variations": [
    {
      "value": true,
      "name": "Enabled"
    },
    {
      "value": false,
      "name": "Disabled"
    }
  ],
  "defaults": {
    "onVariation": 0,
    "offVariation": 1
  }
}
```

### Field Descriptions

| Field | Description |
|-------|-------------|
| `name` | Human-readable flag name |
| `key` | Unique identifier used in code |
| `description` | Purpose of the flag |
| `temporary` | Whether this is a temporary flag |
| `tags` | Labels for organization |
| `clientSideAvailability` | SDK availability settings |
| `variations` | Possible flag values |
| `defaults` | Default variations for on/off states |

### Python Code

```python
import urllib.request
import json

url = 'https://app.launchdarkly.com/api/v2/flags/arif-skyhigh-releasedemo'

flag_data = {
    "name": "ZipHQ",
    "key": "ziphq",
    "description": "ZipHQ feature flag for release pipeline demo",
    "temporary": True,
    "tags": ["demo", "ziphq"],
    "clientSideAvailability": {
        "usingEnvironmentId": True,
        "usingMobileKey": False
    },
    "variations": [
        {"value": True, "name": "Enabled"},
        {"value": False, "name": "Disabled"}
    ],
    "defaults": {
        "onVariation": 0,
        "offVariation": 1
    }
}

data = json.dumps(flag_data).encode('utf-8')

req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(json.dumps(result, indent=2))
```

### Response

```json
{
  "name": "ZipHQ",
  "kind": "boolean",
  "description": "ZipHQ feature flag for release pipeline demo",
  "key": "ziphq",
  "version": 1,
  "creationDate": 1766084761746,
  "includeInSnippet": true,
  "clientSideAvailability": {
    "usingMobileKey": false,
    "usingEnvironmentId": true
  },
  "variations": [
    {
      "id": "e8bb4752-1574-47aa-a674-2860fbae0cf8",
      "value": true,
      "name": "Enabled"
    },
    {
      "id": "ebde8970-2c0d-4cb1-8048-d9c59b7ac7cf",
      "value": false,
      "name": "Disabled"
    }
  ],
  "temporary": true,
  "tags": ["demo", "ziphq"],
  "archived": false,
  "deprecated": false,
  "defaults": {
    "onVariation": 0,
    "offVariation": 1
  },
  "environments": {
    "dev": {
      "on": false,
      "version": 1,
      "rules": [],
      "fallthrough": { "variation": 0 },
      "offVariation": 1
    },
    "qa": {
      "on": false,
      "version": 1,
      "rules": [],
      "fallthrough": { "variation": 0 },
      "offVariation": 1
    },
    "int": {
      "on": false,
      "version": 1,
      "rules": [],
      "fallthrough": { "variation": 0 },
      "offVariation": 1
    },
    "production": {
      "on": false,
      "version": 1,
      "rules": [],
      "fallthrough": { "variation": 0 },
      "offVariation": 1
    }
  }
}
```

> 📝 **Note**: Save the `variations[].id` values - you'll need the "Enabled" variation ID (`e8bb4752-1574-47aa-a674-2860fbae0cf8`) for the release.

---

## Step 4: Create a New Release Pipeline

Create a dedicated release pipeline for the ZipHQ feature.

### Request

```
POST https://app.launchdarkly.com/api/v2/projects/{projectKey}/release-pipelines
```

### Headers

```
Authorization: <YOUR_API_KEY>
Content-Type: application/json
LD-API-Version: beta
```

### Request Body

```json
{
  "name": "ZipHQ Release Pipeline",
  "key": "ziphq-release-pipeline",
  "description": "Release pipeline for ZipHQ feature",
  "phases": [
    {
      "name": "Dev",
      "audiences": [
        {
          "environmentKey": "dev",
          "name": "Dev"
        }
      ]
    },
    {
      "name": "QA",
      "audiences": [
        {
          "environmentKey": "qa",
          "name": "QA"
        }
      ]
    },
    {
      "name": "Integration",
      "audiences": [
        {
          "environmentKey": "int",
          "name": "Int"
        }
      ]
    },
    {
      "name": "Production",
      "audiences": [
        {
          "environmentKey": "production",
          "name": "Production"
        }
      ]
    }
  ]
}
```

### Python Code

```python
import urllib.request
import json

url = 'https://app.launchdarkly.com/api/v2/projects/arif-skyhigh-releasedemo/release-pipelines'

pipeline_data = {
    "name": "ZipHQ Release Pipeline",
    "key": "ziphq-release-pipeline",
    "description": "Release pipeline for ZipHQ feature",
    "phases": [
        {
            "name": "Dev",
            "audiences": [{"environmentKey": "dev", "name": "Dev"}]
        },
        {
            "name": "QA",
            "audiences": [{"environmentKey": "qa", "name": "QA"}]
        },
        {
            "name": "Integration",
            "audiences": [{"environmentKey": "int", "name": "Int"}]
        },
        {
            "name": "Production",
            "audiences": [{"environmentKey": "production", "name": "Production"}]
        }
    ]
}

data = json.dumps(pipeline_data).encode('utf-8')

req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(json.dumps(result, indent=2))
```

### Response

```json
{
  "createdAt": "2025-12-18T19:07:20.805273524Z",
  "description": "Release pipeline for ZipHQ feature",
  "key": "ziphq-release-pipeline",
  "name": "ZipHQ Release Pipeline",
  "phases": [
    {
      "id": "ec2d2e01-8d90-49a1-8417-02527cbebc77",
      "name": "Dev",
      "audiences": [
        {
          "environment": {
            "key": "dev",
            "name": "Dev",
            "color": "00da7b"
          },
          "name": "Dev",
          "configuration": {
            "releaseStrategy": "",
            "requireApproval": false
          }
        }
      ]
    },
    {
      "id": "91ae0637-8a08-432e-a36a-4a920bbe40ed",
      "name": "QA",
      "audiences": [...]
    },
    {
      "id": "88788d9b-999b-4a19-a49f-ae037eb47149",
      "name": "Integration",
      "audiences": [...]
    },
    {
      "id": "61066305-b150-489a-894c-d577ba6a3f49",
      "name": "Production",
      "audiences": [...]
    }
  ],
  "tags": [],
  "_version": 0,
  "_isLegacy": false
}
```

> 📝 **Important**: Save the phase IDs from the response - you'll need them to start each phase:
> - Dev: `ec2d2e01-8d90-49a1-8417-02527cbebc77`
> - QA: `91ae0637-8a08-432e-a36a-4a920bbe40ed`
> - Integration: `88788d9b-999b-4a19-a49f-ae037eb47149`
> - Production: `61066305-b150-489a-894c-d577ba6a3f49`

---

## Step 5: Add Flag to Release Pipeline

Attach the ZipHQ flag to the newly created release pipeline. This creates a "release" for the flag.

### Request

```
PUT https://app.launchdarkly.com/api/v2/projects/{projectKey}/flags/{flagKey}/release
```

### Headers

```
Authorization: <YOUR_API_KEY>
Content-Type: application/json
LD-API-Version: beta
```

### Request Body

```json
{
  "releasePipelineKey": "ziphq-release-pipeline"
}
```

### Python Code

```python
import urllib.request
import json

url = 'https://app.launchdarkly.com/api/v2/projects/arif-skyhigh-releasedemo/flags/ziphq/release'

release_data = {
    "releasePipelineKey": "ziphq-release-pipeline"
}

data = json.dumps(release_data).encode('utf-8')

req = urllib.request.Request(url, data=data, method='PUT')
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(json.dumps(result, indent=2))
```

### Response

```json
{
  "_links": {
    "parent": {
      "href": "/api/v2/flags/arif-skyhigh-releasedemo/ziphq",
      "type": "application/json"
    },
    "self": {
      "href": "/api/v2/flags/arif-skyhigh-releasedemo/ziphq/release",
      "type": "application/json"
    }
  },
  "name": "ZipHQ Release Pipeline",
  "releasePipelineKey": "ziphq-release-pipeline",
  "releasePipelineDescription": "",
  "phases": [
    {
      "_id": "ec2d2e01-8d90-49a1-8417-02527cbebc77",
      "_name": "Dev",
      "complete": false,
      "_creationDate": 1766084905114,
      "_audiences": [
        {
          "_id": "ea7c0881-a71e-491a-bd6d-5dab0ddad152",
          "environment": {
            "key": "dev",
            "name": "Dev",
            "color": "00da7b"
          },
          "name": "Dev",
          "configuration": {
            "releaseStrategy": "",
            "requireApproval": false
          },
          "status": "ready-to-start"
        }
      ],
      "status": "ready-to-start",
      "started": false
    },
    {
      "_id": "91ae0637-8a08-432e-a36a-4a920bbe40ed",
      "_name": "QA",
      "complete": false,
      "status": "not-started",
      "started": false
    },
    {
      "_id": "88788d9b-999b-4a19-a49f-ae037eb47149",
      "_name": "Integration",
      "complete": false,
      "status": "not-started",
      "started": false
    },
    {
      "_id": "61066305-b150-489a-894c-d577ba6a3f49",
      "_name": "Production",
      "complete": false,
      "status": "not-started",
      "started": false
    }
  ],
  "_version": 0,
  "_releaseVariationId": "e8bb4752-1574-47aa-a674-2860fbae0cf8"
}
```

### Current State After Step 5

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Dev        │ →  │       QA        │ →  │   Integration   │ →  │   Production    │
│ ready-to-start  │    │   not-started   │    │   not-started   │    │   not-started   │
│   (waiting)     │    │    (locked)     │    │    (locked)     │    │    (locked)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Step 6: Start Phase 1 (Dev)

Activate the Dev phase to turn on the flag in the Dev environment.

### Request

```
PUT https://app.launchdarkly.com/api/v2/projects/{projectKey}/flags/{flagKey}/release/phases/{phaseId}
```

### Headers

```
Authorization: <YOUR_API_KEY>
Content-Type: application/json
LD-API-Version: beta
```

### Request Body

```json
{
  "status": "active"
}
```

### Python Code

```python
import urllib.request
import json

# Use the Dev phase ID from Step 4 response
phase_id = 'ec2d2e01-8d90-49a1-8417-02527cbebc77'

url = f'https://app.launchdarkly.com/api/v2/projects/arif-skyhigh-releasedemo/flags/ziphq/release/phases/{phase_id}'

phase_data = {
    "status": "active"
}

data = json.dumps(phase_data).encode('utf-8')

req = urllib.request.Request(url, data=data, method='PUT')
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(json.dumps(result, indent=2))
```

### Response

```json
{
  "_links": {
    "parent": {
      "href": "/api/v2/flags/arif-skyhigh-releasedemo/ziphq",
      "type": "application/json"
    },
    "self": {
      "href": "/api/v2/flags/arif-skyhigh-releasedemo/ziphq/release",
      "type": "application/json"
    }
  },
  "name": "ZipHQ Release Pipeline",
  "releasePipelineKey": "ziphq-release-pipeline",
  "releasePipelineDescription": "Release pipeline for ZipHQ feature",
  "phases": [
    {
      "_id": "ec2d2e01-8d90-49a1-8417-02527cbebc77",
      "_name": "Dev",
      "complete": false,
      "_creationDate": 1766084905114,
      "_audiences": [
        {
          "_id": "ea7c0881-a71e-491a-bd6d-5dab0ddad152",
          "environment": {
            "key": "dev",
            "name": "Dev",
            "color": "00da7b"
          },
          "name": "Dev",
          "configuration": {
            "releaseStrategy": "",
            "requireApproval": false
          },
          "status": "ready-to-start"
        }
      ],
      "status": "active",
      "started": true,
      "_startedDate": 1766085303466
    },
    {
      "_id": "91ae0637-8a08-432e-a36a-4a920bbe40ed",
      "_name": "QA",
      "complete": false,
      "status": "not-started",
      "started": false
    },
    {
      "_id": "88788d9b-999b-4a19-a49f-ae037eb47149",
      "_name": "Integration",
      "complete": false,
      "status": "not-started",
      "started": false
    },
    {
      "_id": "61066305-b150-489a-894c-d577ba6a3f49",
      "_name": "Production",
      "complete": false,
      "status": "not-started",
      "started": false
    }
  ],
  "_version": 1,
  "_releaseVariationId": "e8bb4752-1574-47aa-a674-2860fbae0cf8"
}
```

### Current State After Step 6

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Dev        │ →  │       QA        │ →  │   Integration   │ →  │   Production    │
│    ✅ ACTIVE    │    │   not-started   │    │   not-started   │    │   not-started   │
│  Flag is ON     │    │    (waiting)    │    │    (waiting)    │    │    (waiting)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### What Happened

| Environment | Flag Status | Description |
|-------------|-------------|-------------|
| **Dev** | 🟢 ON | Flag is now enabled in Dev |
| QA | ⚪ OFF | Waiting for Dev to complete |
| Int | ⚪ OFF | Waiting for QA to complete |
| Production | ⚪ OFF | Waiting for Int to complete |

---

## Step 7: Integrate Flag in Your Application

Now that the Dev phase is active and the flag is ON, integrate it into your Flask application.

### 7.1 Add Flag Change Listener

Add a listener to track when the flag value changes:

```python
# In app.py - after existing listeners
ldclient.get().flag_tracker.add_flag_value_change_listener(
    "ziphq", mycontext, changer
)
```

### 7.2 Evaluate Flag in Route

Add the flag evaluation to your home page route:

```python
@app.route("/")
def show_page():
    current_route_rule = str(request.url_rule)
    home_page_slider = ldclient.get().variation(
        "release-home-page-slider", mycontext, False
    )
    coffee_promo_1 = ldclient.get().variation("coffee-promo-1", mycontext, False)
    coffee_promo_2 = ldclient.get().variation("coffee-promo-2", mycontext, False)
    
    # Add ZipHQ flag evaluation
    ziphq_enabled = ldclient.get().variation("ziphq", mycontext, False)
    
    retval = make_response(
        render_template(
            "index.html",
            current_route_rule=current_route_rule,
            home_page_slider=home_page_slider,
            coffee_promo_1=coffee_promo_1,
            coffee_promo_2=coffee_promo_2,
            ziphq_enabled=ziphq_enabled,  # Pass to template
        )
    )
    return retval
```

### 7.3 Create API Endpoint

Add a dedicated API endpoint to check the flag status:

```python
@app.route("/api/ziphq")
def ziphq_status():
    """API endpoint to check ZipHQ feature flag status"""
    ziphq_enabled = ldclient.get().variation("ziphq", mycontext, False)
    return {
        "flag": "ziphq",
        "enabled": ziphq_enabled,
        "context": {
            "user": mycontext.get("user").key,
            "name": mycontext.get("user").get("name")
        }
    }
```

### 7.4 Use Flag in Templates (Optional)

In your Jinja2 templates, you can conditionally show content:

```html
{% if ziphq_enabled %}
    <div class="ziphq-feature">
        <!-- New ZipHQ feature content -->
        <h2>🚀 ZipHQ Feature Enabled!</h2>
    </div>
{% endif %}
```

---

## Step 8: Test the Flag

Verify the flag is working correctly before progressing to the next phase.

### 8.1 Test Script

Run this Python script to verify flag evaluation:

```python
import os
from dotenv import load_dotenv
import ldclient
from ldclient.config import Config

load_dotenv()

ldclient.set_config(Config(os.environ['LD_SDK_KEY']))

if ldclient.get().is_initialized():
    print('✅ SDK initialized successfully!')
    
    context = ldclient.Context.builder('test-user').name('Test User').build()
    
    # Check ziphq flag
    ziphq = ldclient.get().variation('ziphq', context, False)
    print(f'')
    print(f'🚩 ZipHQ Flag Status: {ziphq}')
    print(f'   Expected: True (Dev phase is active)')
    
    if ziphq:
        print(f'')
        print(f'🎉 SUCCESS! The ziphq flag is enabled!')
    else:
        print(f'')
        print(f'⚠️  Flag returned False - check SDK key or phase status')
else:
    print('❌ SDK failed to initialize')

ldclient.get().close()
```

### 8.2 Run the Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python -c "<paste script above>"
```

### 8.3 Expected Output

```
✅ SDK initialized successfully!

🚩 ZipHQ Flag Status: True
   Expected: True (Dev phase is active)

🎉 SUCCESS! The ziphq flag is enabled!
```

### 8.4 Test via API Endpoint

Start the Flask app and test the API:

```bash
# Start the app
source venv/bin/activate
python app.py
```

Then visit: **http://localhost:3000/api/ziphq**

Expected response:
```json
{
  "flag": "ziphq",
  "enabled": true,
  "context": {
    "user": "user-018e7bd4-ab96-782e-87b0-b1e32082b481",
    "name": "Miriam Wilson"
  }
}
```

### Current State After Step 8

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Dev        │ →  │       QA        │ →  │   Integration   │ →  │   Production    │
│    ✅ ACTIVE    │    │   not-started   │    │   not-started   │    │   not-started   │
│  Flag: TRUE     │    │  Flag: FALSE    │    │  Flag: FALSE    │    │  Flag: FALSE    │
│   (tested ✓)    │    │    (waiting)    │    │    (waiting)    │    │    (waiting)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Step 9: Get Release Status

Check the current status of the release at any time.

### Request

```
GET https://app.launchdarkly.com/api/v2/flags/{projectKey}/{flagKey}/release
```

### Headers

```
Authorization: <YOUR_API_KEY>
Content-Type: application/json
LD-API-Version: beta
```

### Python Code

```python
import urllib.request
import json

url = 'https://app.launchdarkly.com/api/v2/flags/arif-skyhigh-releasedemo/ziphq/release'

req = urllib.request.Request(url)
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    print(json.dumps(data, indent=2))
```

---

## Step 10: Complete Phase and Progress to QA

Once testing is complete in Dev, progress to the next phase.

### 10.1 Complete Dev Phase

Mark the Dev phase as complete:

**Request:**
```
PUT https://app.launchdarkly.com/api/v2/projects/{projectKey}/flags/{flagKey}/release/phases/{phaseId}
```

**Request Body:**
```json
{
  "status": "complete"
}
```

**Python Code:**
```python
import urllib.request
import json

# Dev phase ID
phase_id = 'ec2d2e01-8d90-49a1-8417-02527cbebc77'

url = f'https://app.launchdarkly.com/api/v2/projects/arif-skyhigh-releasedemo/flags/ziphq/release/phases/{phase_id}'

phase_data = {
    "status": "complete"
}

data = json.dumps(phase_data).encode('utf-8')

req = urllib.request.Request(url, data=data, method='PUT')
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(json.dumps(result, indent=2))
```

### 10.2 Start QA Phase

After Dev is complete, start the QA phase:

**Python Code:**
```python
import urllib.request
import json

# QA phase ID
qa_phase_id = '91ae0637-8a08-432e-a36a-4a920bbe40ed'

url = f'https://app.launchdarkly.com/api/v2/projects/arif-skyhigh-releasedemo/flags/ziphq/release/phases/{qa_phase_id}'

phase_data = {
    "status": "active"
}

data = json.dumps(phase_data).encode('utf-8')

req = urllib.request.Request(url, data=data, method='PUT')
req.add_header('Authorization', '<YOUR_API_KEY>')
req.add_header('Content-Type', 'application/json')
req.add_header('LD-API-Version', 'beta')

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode())
    print(json.dumps(result, indent=2))
```

### 10.3 Phase IDs Reference

| Phase | Phase ID |
|-------|----------|
| Dev | `ec2d2e01-8d90-49a1-8417-02527cbebc77` |
| QA | `91ae0637-8a08-432e-a36a-4a920bbe40ed` |
| Integration | `88788d9b-999b-4a19-a49f-ae037eb47149` |
| Production | `61066305-b150-489a-894c-d577ba6a3f49` |

### 10.4 Full Release Progression

| Step | Action | Phase ID | Endpoint Body |
|------|--------|----------|---------------|
| 1 | Start Dev | `ec2d2e01-...` | `{"status": "active"}` |
| 2 | Complete Dev | `ec2d2e01-...` | `{"status": "complete"}` |
| 3 | Start QA | `91ae0637-...` | `{"status": "active"}` |
| 4 | Complete QA | `91ae0637-...` | `{"status": "complete"}` |
| 5 | Start Int | `88788d9b-...` | `{"status": "active"}` |
| 6 | Complete Int | `88788d9b-...` | `{"status": "complete"}` |
| 7 | Start Prod | `61066305-...` | `{"status": "active"}` |
| 8 | Complete Prod | `61066305-...` | `{"status": "complete"}` |

### State After Completing All Phases

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Dev        │ →  │       QA        │ →  │   Integration   │ →  │   Production    │
│   ✅ COMPLETE   │    │   ✅ COMPLETE   │    │   ✅ COMPLETE   │    │   ✅ COMPLETE   │
│  Flag: TRUE     │    │  Flag: TRUE     │    │  Flag: TRUE     │    │  Flag: TRUE     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

🎉 Release Complete! Flag is now enabled in all environments.
```

---

## Phase Statuses Reference

| Status | Description |
|--------|-------------|
| `ready-to-start` | Phase can be started |
| `active` | Phase is currently running, flag is ON in this environment |
| `complete` | Phase has finished successfully |
| `not-started` | Previous phases must complete first |

---

## Additional API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Delete Release | DELETE | `/api/v2/projects/{projectKey}/flags/{flagKey}/release` |
| Patch Release | PATCH | `/api/v2/projects/{projectKey}/flags/{flagKey}/release` |
| List Feature Flags | GET | `/api/v2/flags/{projectKey}` |
| Get Feature Flag | GET | `/api/v2/flags/{projectKey}/{flagKey}` |
| Delete Feature Flag | DELETE | `/api/v2/flags/{projectKey}/{flagKey}` |
| List Pipelines | GET | `/api/v2/projects/{projectKey}/release-pipelines` |
| Delete Pipeline | DELETE | `/api/v2/projects/{projectKey}/release-pipelines/{pipelineKey}` |

---

## Quick Reference: ZipHQ Release IDs

| Resource | Key/ID |
|----------|--------|
| Project | `arif-skyhigh-releasedemo` |
| Flag Key | `ziphq` |
| Pipeline Key | `ziphq-release-pipeline` |
| Dev Phase ID | `ec2d2e01-8d90-49a1-8417-02527cbebc77` |
| QA Phase ID | `91ae0637-8a08-432e-a36a-4a920bbe40ed` |
| Int Phase ID | `88788d9b-999b-4a19-a49f-ae037eb47149` |
| Prod Phase ID | `61066305-b150-489a-894c-d577ba6a3f49` |
| Release Variation ID | `e8bb4752-1574-47aa-a674-2860fbae0cf8` |

---

## LaunchDarkly UI Links

- **Flag**: [app.launchdarkly.com/.../features/ziphq](https://app.launchdarkly.com/arif-skyhigh-releasedemo/dev/features/ziphq)
- **Releases**: [app.launchdarkly.com/.../releases](https://app.launchdarkly.com/projects/arif-skyhigh-releasedemo/releases)

---

## References

- [LaunchDarkly Releases Beta API](https://launchdarkly.com/docs/api/releases-beta/)
- [LaunchDarkly Release Pipelines API](https://launchdarkly.com/docs/api/release-pipelines-beta/)
- [LaunchDarkly MCP Server](https://github.com/launchdarkly/mcp-server)
- [LaunchDarkly Python SDK](https://docs.launchdarkly.com/sdk/server-side/python)

---

*Generated on: December 18, 2025*
