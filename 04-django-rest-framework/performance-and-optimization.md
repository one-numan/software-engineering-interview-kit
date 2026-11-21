# DRF Performance & Query Optimization Guide

## Module Overview
This module covers high-throughput **DRF Performance Tuning**, eliminating serializer overhead, pre-fetching data, and optimizing JSON rendering.

---

## The 4 Rules of High-Performance DRF Endpoints

1. **Defer and Only:** Never fetch columns you do not return. If a table has a 5MB `raw_payload` text field, use `defer()`:
   ```python
   # Excludes heavy text columns from SELECT query
   queryset = Article.objects.defer("raw_content").all()
   ```
2. **Values and Values_list for Read-Only APIs:** If an endpoint only returns simple read-only data, bypass model instantiation completely:
   ```python
   # 4x faster than Serializer(Model.objects.all())
   data = list(Order.objects.values("id", "total_amount", "status"))
   return Response(data)
   ```
3. **Always Preload Foreign Keys:** Use `select_related()` for ForeignKey/OneToOne and `prefetch_related()` for ManyToMany.
4. **Use `UJSONRenderer` or `ORJSONRenderer`:** Replace standard Python JSON rendering with Rust-backed `orjson` to achieve $5\times$ faster JSON serialization.
