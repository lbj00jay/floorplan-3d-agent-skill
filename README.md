# 图片转可编辑户型 · floorplan-image

基于 [wy51ai/floorplan-3d](https://github.com/wy51ai/floorplan-3d)，上游提交 `730ec0923a018fdf38b4687c5ef385c7dcac451f`。保留原作者 `Copyright (c) 2026 wuyi` 及 MIT 许可证；新增 Agent Skill、完整户型加载、几何数据编辑、校验与单文件生成。原英文功能说明保留在 README.en.md。

## 使用方式

将 `skills/floorplan-image` 文件夹复制到 Agent 的技能目录，例如 `~/.codex/skills/floorplan-image`。对有视觉能力的 Codex/Agent 输入一张清晰平面户型图，并说：

> 使用 $floorplan-image，把这张图还原成可编辑的 2D/3D 户型页面。按原图映射家具类型、位置、朝向与尺寸；区分实测和估计，输出 HTML、JSON 和叠图。

Agent 根据 SKILL.md 识别图片，再运行 Python 脚本。HTML 自身不调用 AI API，也不包含 API 密钥。当前无需训练或部署模型。单张室内实景照不能唯一恢复完整户型，当前几何仅支持正交墙体。

## 不通过 Agent，直接加载数据

```sh
python3 skills/floorplan-image/scripts/plan_tools.py validate examples/two-room.json
python3 skills/floorplan-image/scripts/plan_tools.py build examples/two-room.json --output outputs/two-room.html
python3 -m http.server 18763 --bind 127.0.0.1
```

浏览器访问 `/outputs/two-room.html`。根目录 `index.html` 仍可直接打开查看原始示例，也可从“文件 → 导入方案”加载任意完整计划。

- 家具：拖动、旋转、调整宽深，在2D和3D之间同步。
- 建筑：文件 → 编辑户型数据，修改房间多边形、墙矩形、门窗；可撤销。
- 导出方案包含完整建筑、家具、拆墙和测量；导入和刷新恢复。旧版仅家具 JSON 不再接收。
- 墙体未知承重属性用 `u`，页面不允许直接拆除。
- 生成单文件内嵌计划和完整 MIT 许可；Three.js 通过 CDN 加载，3D需要联网。

数据协议与家具映射见 `skills/floorplan-image/references/`。生成器仅依赖 Python3.8+ 标准库。技能模板 `assets/index.html` 应与根目录 HTML 保持一致，测试会检查。

## 验证

```sh
python3 -m unittest discover -s tests -v
```

浏览器集成验收：安装 `playwright` 及匹配的 Chromium，然后运行 `python3 tests/browser_smoke.py`。脚本启动独立临时端口和无登录浏览器，检查完整计划切换、几何与家具修改、导入导出、撤销、刷新恢复和3D渲染。结果与截图保存于 gitignored `outputs/`。

合成样例只验证工程链路，不代表真实图片识别准确率。真实质量需使用用户图片逐张叠图复核；无尺度输入的面积/造价仅为估计。窗台高度和家具细节主要采用模板默认值。

## 开源与发布

本项目采用 MIT 许可证，允许修改、再发布与商用。分发时保留原作者版权声明和完整 LICENSE；生成的HTML也内嵌许可证与来源链接。引用第三方图片的权限须单独处理。
