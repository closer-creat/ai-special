此次合并引入了一个完整的小说爬虫项目，包含前端界面、后端服务和爬虫功能，支持多个小说网站的内容爬取和多种格式输出。项目结构完整，包含规范文档、核心爬虫代码、Web界面和测试文件。
| 文件 | 变更 |
|------|---------|
| .trae/specs/novel-crawler/checklist.md | - 新增检查清单文件，包含项目开发的各个阶段检查项 |
| .trae/specs/novel-crawler/spec.md | - 新增规格说明文件，详细描述项目的功能需求和技术方案 |
| .trae/specs/novel-crawler/tasks.md | - 新增任务清单文件，分解项目开发的具体任务 |
| example_usage.py | - 新增示例使用文件，展示如何使用小说爬虫 |
| novel_crawler.log | - 新增日志文件，记录爬虫运行过程中的信息 |
| novel_crawler.py | - 新增小说爬虫主文件，实现基础爬虫功能 |
| novel_crawler/app.py | - 新增Flask应用文件，提供Web界面和API接口 |
| novel_crawler/main.py | - 新增主文件，实现命令行接口 |
| novel_crawler/requirements.txt | - 新增依赖文件，列出项目所需的Python包 |
| novel_crawler/spiders/base_spider.py | - 新增基础爬虫文件，实现通用爬虫功能 |
| novel_crawler/spiders/novel_spider.py | - 新增小说爬虫文件，实现具体网站的爬取逻辑 |
| novel_crawler/templates/index.html | - 新增前端模板文件，提供用户友好的Web界面 |
| novel_crawler/utils/file_utils.py | - 新增文件工具文件，实现文件保存功能 |
| test_crawler.py | - 新增测试文件，测试爬虫的错误处理与重试机制 |
| test_crawler_optimizations.py | - 新增优化测试文件，测试爬虫的性能优化效果 |