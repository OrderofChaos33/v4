# Changelog

All notable changes to the 280E Expense Reclassification MVP will be documented in this file.

## [0.1.0] - 2024-01-04

### Added
- Initial MVP release
- FastAPI-based REST API for GL analysis
- CSV parser with flexible column mapping
- Rule-based 280E classification engine with confidence scoring
- PDF report generation with executive summary and detailed breakdown
- CSV and JSON export options
- Mock LLM integration points for future enhancement
- Comprehensive test suite (16 tests)
- API documentation (Swagger/ReDoc)
- Setup and usage documentation
- Sample GL data for testing
- Legal disclaimer in all reports
- Audit trail and rationale tracking
- Automatic flagging of low-confidence items

### Features
- POST /api/analyze - Upload and analyze GL data
- GET /api/report/{id} - Retrieve full analysis
- GET /api/report/{id}/pdf - Download PDF report
- GET /api/report/{id}/csv - Download CSV export
- GET /api/report/{id}/json - Download JSON export
- DELETE /api/report/{id} - Cleanup endpoint

### Classification Categories
- Cost of Goods Sold (COGS) - Deductible
- Deductible Operating Expenses - May be deductible
- Non-Deductible (280E) - Subject to restrictions

### Known Limitations
- In-memory storage only (no persistence)
- Mock LLM logic (placeholder for real AI)
- Single-entity focus (multi-entity requires enhancement)
- No user authentication
- No real-time collaboration features
- No integration with accounting software APIs

### Coming Soon (TODOs)
- Real LLM integration (OpenAI/Anthropic)
- Database persistence (PostgreSQL/MongoDB)
- User authentication and multi-tenant support
- Manual override/review interface
- State-specific classification rules
- Multi-entity structure support
- QuickBooks/NetSuite API integration
- Historical comparison reports
- Batch processing for large files

## Future Versions

### [0.2.0] - Planned
- Real LLM integration
- Persistent database storage
- Enhanced confidence scoring
- More sophisticated COGS allocation

### [0.3.0] - Planned
- User authentication
- Multi-tenant support
- Manual override interface
- Audit log export

### [1.0.0] - Planned
- Production-ready features
- Full multi-entity support
- API integrations
- Advanced analytics
- CPA collaboration tools
