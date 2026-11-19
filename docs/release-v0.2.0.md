## Mouse Battery Tray v0.2.0

Windows tray battery meter for the verified **VGN 2.4G receiver `3554:F503`**.

### 新功能 / What's new

- 托盘右键菜单新增 **Always show on taskbar**，可将电量图标放到时钟旁。
- 启动时恢复常驻偏好；只调整本程序的图标，不重启资源管理器。
- 增加 Windows 任务栏设置入口，以及 `install.ps1 -ShowOnTaskbar` 安装选项。
- 提供 Windows 可执行文件、便携 ZIP、Python wheel / 源码包和 SHA-256 校验文件。

### 下载 / Downloads

- **Windows x64**: download `MouseBatteryTray.exe`, or extract the portable ZIP and run the EXE.
- **Python users**: download the `.whl` and run `py -m pip install <downloaded-wheel>`.
- **Source**: use the source archive or clone this repository.
- Verify downloads using `SHA256SUMS.txt` and Windows PowerShell `Get-FileHash -Algorithm SHA256`.

无需管理员权限。Windows 可能先将图标放入 `^` 区域；右键开启 **Always show on taskbar**。
需要登录时自动启动，可再开启 **Start with Windows**（建议先安装到固定目录）。

### Limits / 已知限制

- Only receiver `3554:F503` is verified; the retail mouse model remains unconfirmed.
- Taskbar promotion uses an internal Windows 11 preference. If unavailable, use **Open Windows taskbar settings**.
- Charging transitions and polling's impact on battery life have not been hardware-validated.
- Windows builds are unsigned. Notifications follow Windows notification / Do Not Disturb settings.
- The first public binary is built and tested locally on Windows 11 x64 / Python 3.13.

### Packaging

GitHub Packages does not provide a PyPI registry. This release distributes the
Windows executable and Python distributions as Release assets. No container or
unrelated package registry is required to use the application.
