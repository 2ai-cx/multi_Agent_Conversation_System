# 🤖 Goose Quick Start Guide

## 📚 **Available Goose Guides**

We have **4 deployment guides** - 2 for humans, 2 for Goose:

| Guide | For | Purpose |
|-------|-----|---------|
| `LOCAL-SETUP-GUIDE.md` | 👤 Human | Detailed local setup instructions |
| `GOOSE-LOCAL-SETUP.md` | 🤖 Goose | Automated local setup |
| `AZURE-DEPLOYMENT-GUIDE.md` | 👤 Human | Detailed Azure deployment |
| `GOOSE-AZURE-DEPLOY.md` | 🤖 Goose | Automated Azure deployment |

---

## 🚀 **Quick Start: Local Setup with Goose**

### **Option 1: Copy-Paste Prompt**

Open Goose and paste this:

```
Please set up the Multi-Agent Timesheet System on this computer by following the guide in GOOSE-LOCAL-SETUP.md. Execute all 11 steps in order:

1. Check and install Python 3.11
2. Clone or update the repository
3. Create Python virtual environment
4. Install all dependencies
5. Start Temporal server in Docker
6. Create .env configuration file
7. Create database setup script
8. Run unit tests to verify installation
9. Create startup script
10. Run verification script
11. Generate user instructions

After completing all steps, show me the contents of SETUP_COMPLETE.md
```

### **Option 2: Direct File Reference**

```
Read GOOSE-LOCAL-SETUP.md and execute all steps in order. Generate SETUP_COMPLETE.md when done.
```

---

## ☁️ **Quick Start: Azure Deployment with Goose**

### **Option 1: Copy-Paste Prompt**

Open Goose and paste this:

```
Please deploy the Multi-Agent Timesheet System to Azure by following the guide in GOOSE-AZURE-DEPLOY.md. Execute all 12 steps in order:

1. Verify Azure login and ACR access
2. Check existing Key Vault secrets
3. Create script for adding missing secrets
4. Build Docker image with timestamp tag
5. Push image to Azure Container Registry
6. Update Azure Container App with new image
7. Verify Key Vault access for managed identity
8. Update environment variables
9. Test the deployment (health, system info, Temporal)
10. Retrieve recent logs
11. Verify Opik tracking is enabled
12. Generate deployment report

After completing all steps, show me the contents of DEPLOYMENT_REPORT.md
```

### **Option 2: Direct File Reference**

```
Read GOOSE-AZURE-DEPLOY.md and execute all steps in order. Generate DEPLOYMENT_REPORT.md when done.
```

---

## 🎯 **What Goose Will Do**

### **Local Setup (GOOSE-LOCAL-SETUP.md)**

Goose will automatically:
- ✅ Install Python 3.11 (if needed)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start Temporal server in Docker
- ✅ Create `.env` file with placeholders
- ✅ Create database setup SQL script
- ✅ Create startup scripts
- ✅ Run tests to verify setup
- ✅ Generate user instructions

**You still need to:**
- 📝 Update API keys in `.env`
- 📝 Run SQL script in Supabase

### **Azure Deployment (GOOSE-AZURE-DEPLOY.md)**

Goose will automatically:
- ✅ Verify Azure authentication
- ✅ Check Key Vault secrets
- ✅ Build Docker image
- ✅ Push to Azure Container Registry
- ✅ Update Container App
- ✅ Configure Key Vault access
- ✅ Set environment variables
- ✅ Test deployment
- ✅ Generate deployment report

**You still need to:**
- 📝 Be logged into Azure (`az login`)
- 📝 Have API keys in Key Vault

---

## 📋 **Prerequisites**

### **For Local Setup:**
```bash
# Check prerequisites
python3.11 --version  # or python3 --version
docker --version
git --version
```

### **For Azure Deployment:**
```bash
# Check prerequisites
az --version
docker --version
az account show  # Must be logged in
```

---

## 🔄 **Re-deployment Shortcuts**

### **Local: Quick Restart**
```bash
./start_server.sh
```

### **Azure: Quick Deploy**
```bash
./quick_deploy.sh
```

Or ask Goose:
```
Run the quick_deploy.sh script to redeploy to Azure
```

---

## 🐛 **Troubleshooting with Goose**

### **Local Issues**

Ask Goose:
```
Run the verify_setup.sh script and diagnose any issues found
```

### **Azure Issues**

Ask Goose:
```
Run the troubleshoot.sh script and help me fix any deployment issues
```

---

## 📊 **What Gets Created**

### **Local Setup Files:**
- `.env` - Environment configuration
- `setup_database.sql` - Database schema
- `start_server.sh` - Server startup script
- `verify_setup.sh` - Setup verification
- `SETUP_COMPLETE.md` - User instructions

### **Azure Deployment Files:**
- `add_secrets.sh` - Secret management
- `quick_deploy.sh` - Fast redeployment
- `troubleshoot.sh` - Diagnostics
- `DEPLOYMENT_REPORT.md` - Deployment summary
- `.last_build_tag` - Build tracking
- `.last_build_image` - Image tracking

---

## 💡 **Tips for Using Goose**

### **1. Let Goose Run Completely**
Don't interrupt Goose mid-execution. Let it complete all steps.

### **2. Review Generated Files**
After Goose finishes, review:
- `SETUP_COMPLETE.md` (local)
- `DEPLOYMENT_REPORT.md` (Azure)

### **3. Manual Steps**
Goose will tell you what you need to do manually (API keys, etc.)

### **4. Iterative Fixes**
If something fails, ask Goose:
```
The deployment failed at step X. Please diagnose and fix the issue.
```

### **5. Verification**
Always verify with:
```
Run the verification/troubleshooting script and confirm everything is working
```

---

## 🎓 **Example Goose Sessions**

### **Session 1: First-Time Local Setup**

```
User: Read GOOSE-LOCAL-SETUP.md and set up the system locally

Goose: [Executes all 11 steps]
      ✅ Python installed
      ✅ Virtual environment created
      ✅ Dependencies installed
      ✅ Temporal started
      ✅ Configuration files created
      
      Here's SETUP_COMPLETE.md:
      [Shows instructions]
      
      You need to:
      1. Update .env with your API keys
      2. Run setup_database.sql in Supabase

User: I've updated the API keys. Can you verify the setup?

Goose: [Runs verify_setup.sh]
      ✅ All checks passed
      Ready to start server!
```

### **Session 2: Azure Deployment**

```
User: Read GOOSE-AZURE-DEPLOY.md and deploy to Azure

Goose: [Executes all 12 steps]
      ✅ Azure authenticated
      ✅ Image built: 1.0.0-20251202-233000
      ✅ Pushed to ACR
      ✅ Container app updated
      ✅ Tests passed
      
      Here's DEPLOYMENT_REPORT.md:
      [Shows deployment details]
      
      Deployment URL:
      https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io

User: Can you test the health endpoint?

Goose: [Runs health check]
      ✅ Status: healthy
      ✅ All agents ready
      ✅ Temporal connected
```

---

## 🆘 **Common Goose Commands**

```bash
# Local setup
"Set up the system locally using GOOSE-LOCAL-SETUP.md"

# Azure deployment
"Deploy to Azure using GOOSE-AZURE-DEPLOY.md"

# Verify setup
"Run verify_setup.sh and show me the results"

# Troubleshoot
"Run troubleshoot.sh and help me fix any issues"

# Quick redeploy
"Run quick_deploy.sh to redeploy the latest changes"

# Check logs
"Show me the last 50 lines of Azure container logs"

# Test endpoints
"Test all the API endpoints and show me the results"
```

---

## ✅ **Success Indicators**

### **Local Setup Success:**
- ✅ `verify_setup.sh` shows all green checks
- ✅ Server starts without errors
- ✅ `curl http://localhost:8003/health` returns 200

### **Azure Deployment Success:**
- ✅ `DEPLOYMENT_REPORT.md` shows "SUCCESS"
- ✅ Health endpoint returns 200
- ✅ No errors in logs
- ✅ Opik tracking enabled

---

## 📞 **Need Help?**

### **Ask Goose:**
```
I'm having trouble with [specific issue]. Can you help diagnose and fix it?
```

### **Check Documentation:**
- Local issues: See `LOCAL-SETUP-GUIDE.md`
- Azure issues: See `AZURE-DEPLOYMENT-GUIDE.md`

### **Run Diagnostics:**
```
Run the troubleshooting script and explain what each issue means
```

---

**🚀 You're ready to use Goose for automated deployment!**

**Start with:**
```
Read GOOSE-LOCAL-SETUP.md and set up the system on this computer
```

**Or:**
```
Read GOOSE-AZURE-DEPLOY.md and deploy to Azure
```
