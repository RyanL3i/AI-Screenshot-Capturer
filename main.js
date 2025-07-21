const { app, BrowserWindow, globalShortcut, ipcMain } = require("electron");
const path = require("path");
const { exec } = require("child_process");

let win;
let isVisible = true;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 500,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile("index.html");
}

app.whenReady().then(() => {
  createWindow();

  // ⌘ + B: toggle overlay visibility
  globalShortcut.register("CommandOrControl+B", () => {
    if (isVisible) {
      win.hide();
    } else {
      win.show();
    }
    isVisible = !isVisible;
  });

  // ⌘ + Enter: capture screenshot + GPT
  globalShortcut.register("CommandOrControl+Return", () => {
  // Step 1: hide overlay
  win.hide();

  setTimeout(() => {
    // Step 2: capture screenshot
    exec("python3 capture_screenshot.py", (err, stdout, stderr) => {
      if (err) {
        win.webContents.send("display-error", stderr || err.message);
        win.show();
        return;
      }

      const screenshotPath = stdout.trim();
      const resolvedPath = "file://" + path.resolve(screenshotPath);

      // Step 3: show Electron window again IMMEDIATELY
      win.show();

      // Step 4: show loading state + start GPT request
      win.webContents.send("display-image", resolvedPath);

      exec(`python3 ai_vision.py "${screenshotPath}"`, (err, stdout, stderr) => {
        if (err || stderr) {
          win.webContents.send("display-error", stderr || err.message);
        } else {
          win.webContents.send("display-response", stdout);
        }
        // ❌ DO NOT hide/show here — already visible
      });
    });
  }, 500); // ensure it's fully hidden for capture
});

});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});
