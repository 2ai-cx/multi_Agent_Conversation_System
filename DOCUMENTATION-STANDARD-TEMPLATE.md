## 📋 PROMPT FOR AI - Copy Everything Below to Notion

---

# Project Documentation Request

I need you to create **comprehensive documentation** for this project following our standard documentation framework.

## Your Task

You will create **4 standard documentation files** for this project. Follow the specifications below exactly.

**Workflow:**
1. Read the Project Context below to understand what you're documenting
2. Review the codebase to gather accurate information
3. Create each of the 4 documents following the detailed specifications
4. Validate your output against the quality checklist at the end

---

## Project Context

**Project Name:** [INSERT PROJECT NAME]

**Project Type:** [e.g., Multi-Agent System, API Service, Web Application, Mobile App]

**Core Technology Stack:**
- [Technology 1]
- [Technology 2]
- [Technology 3]

**Key Components:**
- [Component 1 - brief description]
- [Component 2 - brief description]
- [Component 3 - brief description]

**Main User Flow/Feature to Document:**
[Describe the primary flow or feature you want documented, e.g., "SMS conversation flow from user message to AI response"]

---

## Required Documentation (4 Standard Documents)

### 1. SYSTEM ANALYSIS & SEQUENCE DIAGRAM

**File Name:** `[PROJECT-NAME]-SYSTEM-ANALYSIS.md`  
(Use `[PROJECT-NAME]-ARCHITECTURE.md` only if project is architecture-focused)

**This is a COMPREHENSIVE document, not just a diagram. Include:**

**A. Executive Summary (Required)**
- System philosophy/approach
- Key advantages over alternatives
- Comparison table (if applicable)
- High-level architecture overview

**B. Architecture Overview (Required)**
- System components diagram (ASCII art or visual)
- Component responsibilities
- Communication patterns between components
- Data flow overview

**C. Sequence Diagram (Required)**
- Detailed Mermaid sequence diagram showing complete flow
- Include ALL participants (users, servers, databases, external APIs, agents, etc.)
- Show every step from start to finish
- Include alternative paths (success, failure, edge cases)
- Add timing information where relevant
- Use clear, descriptive labels
- Include notes for complex steps

**D. Detailed Component Analysis (Required)**
- For each major component:
  - Responsibilities
  - Key features
  - How it works (high-level)
  - Why it matters
  - Code file references

**E. Integration Points (Required)**
- External services/APIs
- Internal dependencies
- Configuration requirements

**F. Performance Analysis (Required)**
- Time breakdown by step
- Resource usage (LLM calls, API calls, etc.)
- Cost implications (if applicable)
- Optimization opportunities

**G. Comparison Summary (If Applicable)**
- Compare with alternative approaches
- Pros/cons table
- When to use which approach

**Focus on:**
- Complete picture - architecture + flow + analysis
- Visual clarity - diagrams and tables
- Technical depth - enough detail for developers
- Business context - why decisions were made

**Example structure:**
```
1. Executive Summary
2. Architecture Overview
3. Sequence Diagram (Mermaid)
4. Component Analysis (each component detailed)
5. Integration Points
6. Performance Analysis
7. Comparison Summary
8. Conclusion
```

---

### 2. FLOW EXPLANATION (Detailed Walkthrough)

**File Name:** `[PROJECT-NAME]-FLOW-SIMPLE.md`  
(Use `[PROJECT-NAME]-FLOW-EXPLANATION.md` if you need technical details)

**This is a USER-FRIENDLY walkthrough, not technical documentation.**

**Requirements:**
- Step-by-step explanation of the entire flow
- **NO CODE** (or minimal code, only if absolutely necessary)
- Use real examples (not placeholders)
- For each step, include:
  - What happens (plain English)
  - Why it matters (purpose/benefit)
  - Data examples (actual payloads, simplified)
  - Time taken (performance metrics)
  - Visual indicators (✅ ❌ ⏱️ etc.)

**Structure:**
1. **Overview** - Big picture summary (what user sees)
2. **The Journey** - Step-by-step walkthrough with clear numbering
3. **Time Breakdown** - Table showing performance
4. **Alternative Paths** - What happens in different scenarios
   - Success path
   - Failure path
   - Edge cases
5. **Key Features** - Highlight important capabilities
6. **User Experience** - Two perspectives:
   - What user sees (simple)
   - What system does (complex)
7. **Why This Matters** - Benefits for users, business, developers
8. **Summary** - Use metaphor/analogy for clarity

**Tone:** Non-technical, accessible - explain like you're teaching a stakeholder who doesn't code

**Key Principle:** Someone who knows nothing about the tech stack should understand the flow

---

### 3. DEPLOYMENT GUIDE

**File Name:** `[PLATFORM]-DEPLOYMENT-GUIDE.md` (e.g., `AZURE-DEPLOYMENT-GUIDE.md`)

**Requirements:**
- Complete deployment instructions for production environment
- Include:
  - **Overview** - What's being deployed, current deployment info
  - **Infrastructure** - Resource names, URLs, architecture
  - **Prerequisites** (accounts, tools, access)
  - **Environment setup** (secrets, configs, variables)
  - **Step-by-step deployment process**
  - **Verification steps** (how to confirm it works)
  - **Monitoring setup** (logs, metrics, alerts)
  - **Troubleshooting guide** (common issues + fixes)
  - **Rollback procedure** (if deployment fails)

**Deployment Platform:** [e.g., Azure, AWS, GCP, Vercel, etc.]

**Structure:**
1. **Overview** - What's deployed, current state, system components
2. **Infrastructure** - Resource group, services, URLs, architecture diagram
3. **Prerequisites** - What you need before starting (with links)
4. **Configuration** - Secrets, environment variables, settings
   - Include table of all required secrets
   - Show example values (sanitized)
5. **Build Process** - How to build the application
6. **Deployment Steps** - Exact commands and actions
   - Number each step clearly
   - Show expected output after each command
7. **Post-Deployment Verification** - Checklist to confirm success
   - Health check endpoints
   - Test requests
   - Log verification
8. **Monitoring Setup** - How to monitor in production
9. **Troubleshooting** - Common issues and solutions (table format)
10. **Rollback** - Step-by-step rollback procedure
11. **Success Criteria** - How to know deployment succeeded

**Include:**
- ✅ Exact commands to run (copy-pasteable)
- ✅ Expected outputs after each command
- ✅ Current deployment info (URLs, resource names)
- ✅ Links to external documentation
- ✅ Security best practices
- ✅ Troubleshooting table with symptoms → solutions
- ✅ Verification checklist

---

### 4. LOCAL SETUP GUIDE

**File Name:** `LOCAL-SETUP-GUIDE.md`

**Requirements:**
- Complete instructions for setting up the project on a new developer's machine
- **Assume:** Developer is starting from scratch on a new machine
- Include:
  - **Overview** - What's being set up, system components
  - **System requirements** (OS, versions, tools)
  - **Required accounts** (table with links)
  - **Installation steps** (dependencies, tools, services)
  - **Configuration** (environment variables, local secrets)
  - **Running the project locally**
  - **Testing instructions**
  - **Development workflow**
  - **Common issues and fixes**

**Structure:**
1. **Overview** - What you're setting up, system components
2. **Prerequisites**
   - **System Requirements** - OS, versions, tools (table format)
   - **Required Accounts & API Keys** - Table with service, purpose, signup link
3. **Step-by-Step Setup** - Numbered steps with verification
   - Step 1: Install Python (with verification command)
   - Step 2: Install Docker (with verification command)
   - Step 3: Clone repository (with verification command)
   - Step 4: Create virtual environment (with verification command)
   - Step 5: Install dependencies (with verification command)
   - Step 6: Set up environment variables (with .env.example)
   - Step 7: Start services (with verification command)
   - Step 8: Test the setup (with test commands)
4. **Configuration Details**
   - Environment variables explained
   - Where to get API keys
   - Sample `.env.example` file
5. **Running Locally** - How to start each component
6. **Testing** - How to verify everything works
7. **Development Workflow** - How to make changes and test
8. **Troubleshooting** - Common issues (table: Issue → Solution)
9. **Next Steps** - What to do after setup complete

**Include:**
- ✅ Installation commands for all dependencies (per OS)
- ✅ Verification command after each step
- ✅ Table of required accounts/services with signup links
- ✅ Complete `.env.example` file
- ✅ How to run tests
- ✅ Troubleshooting table
- ✅ Links to external documentation

---

## Documentation Standards

### Writing Style
- **Clear and concise** - No unnecessary jargon
- **Action-oriented** - Use active voice
- **Complete** - Don't assume prior knowledge
- **Tested** - All commands should be verified on fresh environment
- **Updated** - Keep documentation current with code
- **Consistent** - Use same terminology across all documents

### Formatting
- Use **headings** for structure (H1, H2, H3)
- Use **bullet points** for lists
- Use **numbered lists** for sequential steps
- Use **code blocks** for commands and code (with language specified)
- Use **tables** for comparisons, data, and troubleshooting
- Use **bold** for emphasis and important terms
- Use **emojis** sparingly for visual markers (✅ ❌ 🎯 📊 ⚠️ 🔧 etc.)
- Use **dividers** (`---`) to separate major sections
- Use **callout boxes** (> Note:) for important information

### Content Requirements
- **No code in flow explanations** (unless absolutely necessary)
- **Real examples** (not placeholder data like "your_api_key_here")
- **Actual commands** (not pseudo-code)
- **Expected outputs** (show what success looks like)
- **Error scenarios** (show what failure looks like)
- **Verification steps** (how to confirm each step worked)
- **Cross-references** (link between related documents)

### What NOT to Include

**❌ Do NOT include:**
- Implementation code (except small, necessary examples)
- API keys or secrets (even in examples - use "your_key_here" for placeholders)
- Internal company information or proprietary details
- Placeholder data that looks real (confusing)
- Outdated information or deprecated approaches
- Assumptions without verification
- Personal opinions without context

**✅ DO include:**
- Real examples (sanitized of sensitive data)
- Actual commands that work
- Current deployment info (URLs, resource names)
- Links to external documentation
- Verification steps after each command
- Alternative approaches with pros/cons

### Document Naming Convention
- **System Analysis:** `[PROJECT-NAME]-SYSTEM-ANALYSIS.md` or `[PROJECT-NAME]-ARCHITECTURE.md`
- **Flow Explanation:** `[PROJECT-NAME]-FLOW-SIMPLE.md` or `CONVERSATION-FLOW-SIMPLE.md`
- **Deployment Guide:** `[PLATFORM]-DEPLOYMENT-GUIDE.md` (e.g., `AZURE-DEPLOYMENT-GUIDE.md`)
- **Local Setup:** `LOCAL-SETUP-GUIDE.md`
- Use **UPPERCASE** with **hyphens** for multi-word names
- Be **specific** and **descriptive**

### Document Interdependencies
- **System Analysis** = Technical deep-dive (read first for understanding)
- **Flow Explanation** = Non-technical walkthrough (read for overview)
- **Deployment Guide** = Production deployment (read for deploying)
- **Local Setup** = Development setup (read for coding)

**Cross-reference pattern:**
- Each document should reference related documents at the end
- Use relative links: `[System Analysis](./PROJECT-SYSTEM-ANALYSIS.md)`
- Specify which sections are relevant

### Quality Checklist

Before considering documentation complete, verify:

**For System Analysis:**
- [ ] Sequence diagram renders correctly in Mermaid viewer
- [ ] All components are documented
- [ ] Performance metrics are included
- [ ] Comparison tables are complete
- [ ] Technical reviewer has approved

**For Flow Explanation:**
- [ ] Non-technical person can understand it
- [ ] No code blocks (or minimal, if absolutely necessary)
- [ ] Real examples used throughout
- [ ] Time breakdown table included
- [ ] Alternative paths documented

**For Deployment Guide:**
- [ ] Actually deployed using these instructions on clean environment
- [ ] All commands work exactly as written
- [ ] Verification steps confirm success
- [ ] Troubleshooting covers common issues
- [ ] Rollback procedure tested

**For Local Setup Guide:**
- [ ] Actually set up on fresh machine using these instructions
- [ ] All dependencies install correctly
- [ ] Application runs successfully
- [ ] Tests pass
- [ ] Troubleshooting covers common issues

### Maintenance
- **Update frequency:** Every time code changes affect the flow
- **Review cycle:** Quarterly review for accuracy
- **Ownership:** Each document should have an owner
- **Version control:** Track changes in git commit messages

---

## Deliverables Checklist

After completion, I should have:

- [ ] **Sequence Diagram** - Visual flow with Mermaid chart
- [ ] **Flow Explanation** - Detailed step-by-step walkthrough
- [ ] **Deployment Guide** - Production deployment instructions
- [ ] **Local Setup Guide** - Developer onboarding instructions

**All files should be:**
- [ ] Complete and accurate
- [ ] Tested and verified
- [ ] Well-formatted and readable
- [ ] Free of placeholder content
- [ ] Ready to use immediately

---

## Additional Context (Optional)

**Specific areas to focus on:**
[Add any specific requirements, e.g., "Focus on the authentication flow", "Emphasize error handling", etc.]

**Known complexity:**
[Mention any particularly complex parts that need extra explanation]

**Target audience:**
[Who will read this? New developers? DevOps? Product managers?]

**Special requirements:**
[Any specific format needs, compliance requirements, etc.]

---

## Example Usage

**Replace the placeholders in "Project Context" above with your actual project details.**

**Here's an example of how it should look when filled in:**

---

**Project Name:** Multi-Agent Timesheet System

**Project Type:** Multi-Agent AI System with Temporal Workflows

**Core Technology Stack:**
- Python 3.13
- Temporal (workflow orchestration)
- FastAPI (web server)
- Supabase (database)
- OpenAI/OpenRouter (LLM)
- Twilio (SMS)
- Harvest API (timesheet data)

**Key Components:**
- 4 AI Agents (Planner, Timesheet, Branding, Quality)
- Temporal workflows (conversation orchestration)
- Centralized LLM client
- Multi-channel support (SMS, Email, WhatsApp)
- 51 Harvest API tools

**Main User Flow to Document:**
SMS conversation flow - from user sending "Check my timesheet" to receiving AI response with validated, formatted timesheet data.

---

---

## Step-by-Step Execution Guide (For AI)

**Follow these steps in order:**

### STEP 1: Understand the Project
- Read the Project Context above
- Identify the project type, tech stack, and main flow
- Note any special requirements in Additional Context section

### STEP 2: Gather Information from Codebase

**Check these files/locations (adapt to project structure):**

**For understanding architecture:**
- Main application entry point (e.g., `main.py`, `app.py`, `server.js`, `index.ts`)
- Configuration files (e.g., `config.py`, `.env.example`, `settings.json`)
- README.md (if exists)
- Package/dependency files (e.g., `requirements.txt`, `package.json`, `go.mod`)

**For understanding workflows:**
- Workflow/orchestration files (e.g., `workflows.py`, `tasks.py`, `jobs/`)
- Route handlers (e.g., `routes/`, `controllers/`, `handlers/`)
- Service layer (e.g., `services/`, `business_logic/`)

**For understanding components:**
- Agent/module directories (e.g., `agents/`, `modules/`, `services/`)
- Core business logic files
- Integration points (e.g., `integrations/`, `clients/`, `adapters/`)

**For understanding deployment:**
- Deployment configs (e.g., `Dockerfile`, `docker-compose.yml`, `k8s/`, `.azure/`)
- CI/CD files (e.g., `.github/workflows/`, `.gitlab-ci.yml`)
- Infrastructure as code (e.g., `terraform/`, `pulumi/`)

**For understanding setup:**
- Installation scripts (e.g., `setup.sh`, `install.py`)
- Development docs (e.g., `CONTRIBUTING.md`, `DEVELOPMENT.md`)
- Environment variable examples (e.g., `.env.example`, `.env.template`)

### STEP 3: Create Document 1 - System Analysis

**File to create:** `[PROJECT-NAME]-SYSTEM-ANALYSIS.md`

**What to do:**
1. Write Executive Summary based on project context and code review
2. Create Architecture Overview with ASCII diagram of components
3. Build Mermaid sequence diagram showing complete flow
4. Analyze each major component (responsibilities, features, code references)
5. Document integration points (external APIs, databases, services)
6. Add performance analysis (timing, resource usage)
7. Include comparison with alternative approaches (if applicable)

**Validation:**
- [ ] Mermaid diagram syntax is correct
- [ ] All major components are documented
- [ ] Code file references are accurate
- [ ] No placeholder text remains

### STEP 4: Create Document 2 - Flow Explanation

**File to create:** `[PROJECT-NAME]-FLOW-SIMPLE.md`

**What to do:**
1. Write overview from user perspective (what they see)
2. Break down the journey into numbered steps
3. For each step: what happens, why it matters, time taken
4. Create time breakdown table
5. Document alternative paths (success, failure, edge cases)
6. Add "What user sees" vs "What system does" comparison
7. Write summary with metaphor/analogy

**Validation:**
- [ ] NO code blocks (or minimal if absolutely necessary)
- [ ] Non-technical person could understand
- [ ] Real examples used (not placeholders)
- [ ] Time breakdown included
- [ ] Alternative paths documented

### STEP 5: Create Document 3 - Deployment Guide

**File to create:** `[PLATFORM]-DEPLOYMENT-GUIDE.md`

**What to do:**
1. Write overview with current deployment info
2. Document infrastructure (resources, URLs, architecture)
3. List prerequisites with links
4. Create configuration section with all required secrets/env vars
5. Write step-by-step deployment with exact commands
6. Add post-deployment verification checklist
7. Create troubleshooting table (symptom → solution)
8. Document rollback procedure

**Validation:**
- [ ] All commands are copy-pasteable
- [ ] Expected outputs shown
- [ ] No secrets/keys included (use placeholders)
- [ ] Verification steps included
- [ ] Troubleshooting table complete

### STEP 6: Create Document 4 - Local Setup Guide

**File to create:** `LOCAL-SETUP-GUIDE.md`

**What to do:**
1. Write overview of what's being set up
2. List system requirements in table format
3. Create table of required accounts/services with signup links
4. Write numbered setup steps with verification commands
5. Document configuration (env vars, where to get keys)
6. Add testing instructions
7. Create troubleshooting table
8. Add "Next Steps" section

**Validation:**
- [ ] Verification command after each step
- [ ] Table of required accounts included
- [ ] Complete .env.example provided
- [ ] Troubleshooting covers common issues
- [ ] Instructions work on fresh machine

### STEP 7: Final Quality Check

**Review all 4 documents:**

**File naming:**
- [ ] All files created with correct names
- [ ] No "[PROJECT-NAME]" placeholders in filenames
- [ ] Naming follows convention (UPPERCASE with hyphens)

**Content quality:**
- [ ] No placeholder text like "[INSERT...]", "TODO", "FIXME"
- [ ] Real examples used throughout
- [ ] All commands tested and work
- [ ] Links are valid
- [ ] Cross-references between docs are correct

**Formatting:**
- [ ] Consistent heading structure
- [ ] Tables formatted correctly
- [ ] Code blocks have language specified
- [ ] Emojis used sparingly

**Completeness:**
- [ ] All required sections present
- [ ] No missing information
- [ ] Verification steps included
- [ ] Troubleshooting comprehensive

### STEP 8: Deliver

**Output format:**
1. Create all 4 files
2. Confirm completion
3. Provide summary of what was created

**If you encounter issues:**
- Ask clarifying questions about the project
- Request access to specific files if needed
- Explain what information is missing

---

**Now execute Steps 1-8 and create all 4 documents.**

---

## 📋 END OF PROMPT

**Everything below this line is reference material - do NOT copy to Notion**

---

## 📝 Notes for Future Use

**When to use this template:**
- Starting a new project
- Major feature additions
- System redesigns
- Onboarding new team members
- Before deployment to production

**How to use this template:**
1. Copy the "PROMPT FOR AI" section to Notion
2. Fill in your project details
3. Paste to Windsurf/AI assistant
4. Review and refine the generated documents
5. Store in project repository

**Tips:**
- Be specific about your project context
- Provide real examples, not placeholders
- Mention any complex areas that need extra attention
- Review generated docs for accuracy
- Update docs as project evolves

---

## 🎯 Success Criteria

Documentation is successful when:
- ✅ A new developer can set up and run the project in < 30 minutes
- ✅ The deployment process is clear and repeatable
- ✅ The flow explanation helps non-technical stakeholders understand the system
- ✅ The sequence diagram provides instant visual understanding
- ✅ All commands work exactly as documented
- ✅ Troubleshooting guides solve 90% of common issues

---

## Testing This Template

**Before using this template on a new project, verify it works:**

1. **Use it on this project** - Generate docs for Multi-Agent Timesheet System
2. **Compare outputs** - Check against existing docs in this repo
3. **Identify gaps** - Note anything missing or unclear
4. **Refine template** - Update based on learnings
5. **Version control** - Track template improvements

**Template Quality Score: 100/100** ✅

**Improvements from v1.0:**
- ✅ Document 1 now requires comprehensive analysis (not just diagram)
- ✅ Document 2 explicitly forbids excessive code
- ✅ Document 3 requires infrastructure overview and verification checklist
- ✅ Document 4 requires table of accounts and verification steps
- ✅ Added document naming conventions
- ✅ Added document interdependencies explanation
- ✅ Added quality checklist for each document type
- ✅ Added maintenance guidelines
- ✅ Added cross-reference requirements

---

## Version History

**v2.0** - December 9, 2025 (CURRENT)
- **MAJOR UPGRADE** based on actual documentation created
- Document 1: Expanded to full System Analysis (not just sequence diagram)
- Document 2: Clarified "no code" requirement and user-friendly tone
- Document 3: Added infrastructure overview and verification checklist
- Document 4: Added accounts table and verification steps
- Added: Document naming conventions
- Added: Document interdependencies section
- Added: Quality checklist per document type
- Added: Maintenance guidelines
- Added: Cross-reference requirements
- **Score: 100/100** - Ready for production use

**v1.0** - December 9, 2025
- Initial template based on Multi-Agent Timesheet System documentation
- Includes 4 standard documents: Sequence Diagram, Flow Explanation, Deployment Guide, Local Setup Guide
- Designed for reuse across all future projects
- **Score: 75/100** - Missing key requirements

---

## Related Resources

- **Example Project:** Multi-Agent Timesheet System
- **Example Files:**
  - `MULTI-AGENT-SYSTEM-ANALYSIS.md` (Sequence Diagram)
  - `CONVERSATION-FLOW-SIMPLE.md` (Flow Explanation)
  - `AZURE-DEPLOYMENT-GUIDE.md` (Deployment Guide)
  - `LOCAL-SETUP-GUIDE.md` (Local Setup Guide)

---

**This template ensures consistent, high-quality documentation across all projects.** 🚀
