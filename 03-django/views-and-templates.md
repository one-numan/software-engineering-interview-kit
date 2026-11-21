# Django Views, Class-Based Views (CBV) & Template Architecture Guide

## Module Overview
This module covers **Django Views (FBV vs CBV)**, generic display and edit views, view mixins, request dispatching, and template context rendering.

---

## Visual Architecture: Function-Based Views (FBV) vs Class-Based Views (CBV)

```mermaid
flowchart TD
    subgraph FBV["Function-Based View (Explicit Control)"]
        Req1[Incoming Request] --> Func[def my_view(request):]
        Func --> IfPost{if request.method == 'POST'}
        IfPost -->|True| FormSave[form.save()]
        IfPost -->|False| Render[render(request, 'template.html')]
    end

    subgraph CBV["Class-Based View (Reusable Object-Oriented Mixins)"]
        Req2[Incoming Request] --> AsView[MyView.as_view()]
        AsView --> Dispatch[dispatch() routes to get() or post()]
        Dispatch --> Mixins[Inherited Mixins: LoginRequired, ContextMixin]
        Mixins --> TemplateResponse[TemplateResponse]
    end
```

---

## Questions & Comprehensive Solutions

### DJ-VIW-001: Function-Based Views (FBV) vs Class-Based Views (CBV)

**Comparison Table:**

| Dimension | Function-Based Views (FBV) | Class-Based Views (CBV) |
| :--- | :--- | :--- |
| **Philosophy** | Explicit, linear, procedural | Reusable, extensible, object-oriented |
| **HTTP Verb Routing**| Explicit `if request.method == 'POST':` conditionals | Automatically dispatches to `get()`, `post()`, `put()`, `delete()` |
| **Code Reuse** | Via Python decorators (`@login_required`) | Via multiple inheritance mixins (`LoginRequiredMixin`, `UserPassesTestMixin`) |
| **Readability** | Very easy to trace line-by-line for beginners | Can suffer from the "hidden logic" problem across deep inheritance hierarchies |
| **Best Used For** | Specialized one-off endpoints, webhook callbacks | Standard CRUD workflows (`ListView`, `DetailView`, `CreateView`, `UpdateView`) |

#### Code Example: Generic `ListView` with QuerySet Filtering

```python
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order

class UserOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        # Enforces user isolation: users only see their own orders
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_spent"] = sum(o.total_amount for o in self.get_queryset())
        return context
```
