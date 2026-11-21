# DRF Pagination & Filtering Architecture Guide

## Module Overview
This module covers **DRF Pagination Classes** (`PageNumberPagination`, `LimitOffsetPagination`, `CursorPagination`) and backend filtering with **`django-filter`**.

---

## Visual Comparison: DRF Pagination Classes

```mermaid
graph TD
    A[DRF Pagination Classes] --> B[PageNumberPagination: ?page=2]
    A --> C[LimitOffsetPagination: ?limit=20&offset=40]
    A --> D[CursorPagination: ?cursor=cD0yMDI2]

    B --> B1[Simple direct jumping; vulnerable to offset performance degradation]
    C --> C1[Client decides limit and offset; standard database style]
    D --> D1[Encrypted opaque cursor; 100% immune to data drift & ultra-fast O(1) index seeks]
```

---

## Questions & Comprehensive Solutions

### DRF-PAG-001: CursorPagination vs PageNumberPagination

**Comparison Table:**

| Feature | `PageNumberPagination` | `CursorPagination` |
| :--- | :--- | :--- |
| **URL Parameter** | `?page=3` | `?cursor=cD0yMDI2LTAxLTAx...` (Base64 token) |
| **Under-the-Hood SQL** | `LIMIT 20 OFFSET 40` | `WHERE created_at < '2026-01-01' ORDER BY created_at DESC LIMIT 20` |
| **Page Drift** | High: Adding items causes duplicates across pages | **Zero: Stable cursor based on position** |
| **Performance** | Degrades as page number increases ($O(N)$) | **Constant $O(1)$ lookup via index** |
| **Page Navigation** | Direct jump to page 10 | Next / Previous buttons only |
| **Best Used For** | Small admin panels | **Social media feeds, high-throughput APIs** |

#### Custom CursorPagination Implementation:

```python
from rest_framework.pagination import CursorPagination

class OrderCursorPagination(CursorPagination):
    page_size = 25
    ordering = '-created_at' # Must be indexed in database!
    cursor_query_param = 'cursor'
```
