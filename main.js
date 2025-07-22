const { app, BrowserWindow, globalShortcut } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

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

  globalShortcut.register("CommandOrControl+B", () => {
    isVisible = !isVisible;
    isVisible ? win.show() : win.hide();
  });

  globalShortcut.register("CommandOrControl+Return", () => {
    const capture = spawn("python3", ["capture_screenshot.py"]);
    let screenshotPath = "";

    capture.stdout.on("data", (data) => {
      screenshotPath += data.toString().trim();
    });

    capture.on("close", () => {
      const resolvedPath = "file://" + path.resolve(screenshotPath);
      win.show();
      win.webContents.send("display-image", resolvedPath);

      const ai = spawn("python3", ["ai_vision.py", screenshotPath]);
      ai.stdout.setEncoding("utf8");

      ai.stdout.on("data", (chunk) => {
        win.webContents.send("stream-chunk", chunk);
      });

      ai.stderr.on("data", (err) => {
        win.webContents.send("display-error", err.toString());
      });
    });
  });
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});
