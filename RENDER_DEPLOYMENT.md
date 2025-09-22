# Render Deployment Guide - Crooks & Castles Command Center V2

## 🚀 **Quick Deployment Steps**

### **1. Upload to GitHub**
```bash
# Initialize git repository
git init
git add .
git commit -m "Crooks & Castles Command Center V2 - Final Working Version"

# Push to GitHub
git remote add origin https://github.com/yourusername/crooks-command-center-v2.git
git push -u origin main
```

### **2. Create Render Web Service**

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub Repository**
4. **Configure Service**:

```
Name: crooks-command-center-v2
Environment: Python 3
Region: Oregon (US West) or closest to your location
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python start.py
```

### **3. Environment Settings**
- **Python Version**: 3.11.x
- **Auto-Deploy**: Yes (recommended)
- **Instance Type**: Starter (free tier) or Professional

### **4. Advanced Settings**
```
Health Check Path: /api/overview
Port: 5000 (auto-detected)
```

## ✅ **Verification Steps**

After deployment, verify these endpoints:

1. **Dashboard**: `https://your-app.onrender.com/`
2. **API Overview**: `https://your-app.onrender.com/api/overview`
3. **Intelligence**: `https://your-app.onrender.com/api/intelligence`
4. **Assets**: `https://your-app.onrender.com/api/assets`
5. **Calendar**: `https://your-app.onrender.com/api/calendar/30`

## 🔧 **Expected Results**

### **Dashboard Metrics**
- Intelligence: 2 sources, 95% trustworthiness
- Assets: 36+ total, 2 categories, 22MB storage
- Calendar: 3 events, $4,700 budget
- Agency: 4 projects, $4,000 budget, 70% completion

### **Performance**
- **Build Time**: ~2-3 minutes
- **Cold Start**: ~10-15 seconds
- **Response Time**: <200ms for all endpoints
- **Memory Usage**: ~150MB

## 🚨 **Troubleshooting**

### **Build Fails**
- Check `requirements.txt` is present
- Verify Python 3.11 compatibility
- Check build logs for missing dependencies

### **App Won't Start**
- Verify `start.py` is present and executable
- Check that `app.py` imports correctly
- Review startup logs for errors

### **Missing Data**
- Ensure `uploads/` directory is included in git
- Verify JSONL files are present in `uploads/intel/`
- Check file permissions

## 📊 **Monitoring**

### **Health Checks**
Render will automatically monitor:
- `/api/overview` endpoint response
- Memory and CPU usage
- Response times

### **Logs**
Access logs via Render dashboard:
- Application logs
- Build logs
- Error tracking

## 🎯 **Production Optimization**

### **For High Traffic**
1. Upgrade to **Professional** instance type
2. Enable **Auto-scaling**
3. Add **CDN** for static assets
4. Configure **Custom Domain**

### **Security**
1. Enable **HTTPS** (automatic on Render)
2. Configure **Environment Variables** for sensitive data
3. Set up **Access Controls** if needed

## 🔄 **Updates**

To deploy updates:
1. Push changes to GitHub
2. Render auto-deploys from main branch
3. Monitor deployment in Render dashboard
4. Verify functionality post-deployment

---

**Deployment Time**: ~5 minutes total
**Ready for Production**: ✅ Yes
**CEO Meeting Ready**: ✅ Absolutely
