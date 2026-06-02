# Google Sheet 部署指南 — 厨师注册自动记录

## 一键部署（2 分钟）

1. 打开这个 Sheet：
   https://docs.google.com/spreadsheets/d/1w4QeyIs40d9aQ0Fd4NTExWKIDm4aV4sr__Av_2lThh0

2. **扩展程序 → Apps Script**（会打开一个新页面）

3. 删除编辑器里的默认代码，粘贴以下内容：

```javascript
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('厨师简历');
    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet('厨师简历');
      sheet.appendRow(['时间戳', '姓名', '电话', '专长', '经验年数', '地区', '期望薪资', '到岗时间', '自我介绍']);
    }
    var now = new Date();
    sheet.appendRow([
      now.toLocaleString('zh-CN', { timeZone: 'Asia/Kuala_Lumpur' }),
      data.name || '', data.phone || '', data.specialty || '',
      data.exp || '', data.location || '', data.salary || '',
      data.available || '', data.desc || ''
    ]);
    return ContentService.createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

4. 点击左上角「**部署**」→「**新建部署**」
   - 类型：**网页应用**
   - 执行身份：**任何人**
   - 有权访问：**任何人**

5. 点击「**部署**」，第一次会弹出授权确认：
   - 选择你的 Google 账号
   - 点「高级」→「前往 jbkitchen...（不安全）」→「允许」

6. 复制生成的 **网址**（像 `https://script.google.com/macros/s/.../exec`）

## 配置网站

把上面的网址填到 `site/layouts/chefs/submit.html` 里的：

```javascript
const GAS_URL = '';
```

改为：

```javascript
const GAS_URL = 'https://script.google.com/macros/s/你复制的网址/exec';
```

然后重新构建部署网站即可。

## 测试

提交一次测试简历，打开 Sheet 看看有没有新增一行。
