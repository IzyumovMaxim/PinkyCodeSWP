

| Quality Attribute | Performance (Time Behavior) |
| :---- | :---- |
| Source | User |
| Stimulus | more than 20 codes of students in .zip file |
| Artifact | PinkyCode server and LLM |
| Environment | Production environment during peak usage period  |
| Response | The system processes all submissions with a delay, however, the correctness of the feedback is still solid  |
| Response Measure  | 95% of the time, end‑to‑end processing for the entire batch completes within 10 seconds; worst‑case (99%) within 30 seconds. |

| Quality Attribute | Reliability (Fault Tolerancy) |
| :---- | :---- |
| Source | User |
| Stimulus | Upload of a non-zip file |
| Artifact | PinkyCode server |
| Environment | Production environment in any period |
| Response | Returns an error window |
| Response Measure  | Fault detected within 30 s, recovery (process back online) within 2 minutes, and no loss of queued requests. |

| Quality Attribute | Maintainability(modifiability) |
| :---- | :---- |
| Source | User |
| Stimulus | To add modifications in different part of architecture(backend, frontend, LLM) |
| Artifact | The entire codebase |
| Environment | The system is running in production or staging, with CI/CD pipeline, version control (Git), and code modularization already in place. |
| Response | Code in each layer can be modified with minimal or no cross-layer dependencies. |
| Response Measure  | No regressions introduced (all previous tests still pass). |

**Performance (Time Behavior)**

To work more effectively, customer will upload many of code simultaneously. The system have to check lots of code’s comments qualitatively and quickly, with no delay. 

**Reliability (Fault Tolerancy)**

The fault of the system have to be easy to fix, so the customer does spend a lot of time to identify the error and possibility to fix them.

**Maintainability(modifiability)**

To update and modify different parts of architecture, they do not have to fail after moderation. It can be little updates that can be made.

**Tests for the first attribute:**

steps to implement:

1)Upload input files

- Upload 21 files simultaneously  
- Timestamp before and after processing.  
- Repeat several times

2)Mesure latency

- Submit 5,10, then 20 files  
- Measure requirement time  
- Analyse latency vs. number of uploaded files


Confirm:

95% of the time, end‑to‑end processing for the entire batch completes within 10 seconds; worst‑case (99%) within 30 seconds.

**Tests for the second attribute:**

steps to implement:

1\) Upload files

\- Upload a zip file with damaged structure.

\- Observe server response (likely error message or silent drop).

\- After error, try a new upload with a valid zip.

Confirm:

Server does not crash  
Processing resumes within 2 minutes  
Logs show controlled exception handling (e.g., try/catch logic)

**Tests for the third attribute:**

- Make a syntax error in LLM area  
     
    
- Push changing to the corresponding branch  
    
- Observe CI pipeline:  
    
  Frontend and Backend components are unchanged and worked

Confirm:

No test failures in frontend/backend areas  
No manual changes needed in other components

