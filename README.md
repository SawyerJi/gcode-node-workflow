# G-code Node Workflow

一个纯前端 G-code 节点工作流工具。

## 工作流

```text
导入模型 G-code
按 Z = 6mm 拆分为 X / Y
导入切割 G-code 作为 Z
输出 X -> G4 S10 -> Z -> G4 S10 -> Y
```

所有 G-code 都在浏览器本地处理，不会上传到服务器。

## 本地打开

直接打开：

```text
index.html
```

或启动本地 HTTP 服务：

```bash
./serve.py --port 8765
```

然后访问：

```text
http://127.0.0.1:8765/
```

## 部署到 Cloudflare Pages

这是静态网站，不需要 Sanity 或后端。

### GitHub

```bash
git add index.html gcode_node_workflow.html README.md
git commit -m "Add G-code node workflow web app"
gh auth login
gh repo create gcode-node-workflow --public --source=. --remote=origin --push
```

### Cloudflare Pages

1. 打开 Cloudflare Dashboard。
2. 进入 `Workers & Pages`。
3. 选择 `Create application`。
4. 选择 `Pages`。
5. 连接刚创建的 GitHub 仓库。
6. 构建设置：

```text
Framework preset: None
Build command: 留空
Build output directory: /
Root directory: /
```

保存后，Cloudflare 会自动部署。以后每次 push 到 GitHub，Cloudflare Pages 都会自动更新网站。

## 文件说明

- `index.html`: 网站入口，会跳转到工具页面。
- `gcode_node_workflow.html`: 节点式交互工具。
- `serve.py`: 本地 HTTP 服务脚本。
- `gcode_workflow.py`: 命令行版 G-code 合并工具。
- `gcode_workflow_spec.md`: 工作流规格说明。
