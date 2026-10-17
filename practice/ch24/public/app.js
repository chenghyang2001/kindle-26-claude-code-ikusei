// 前端邏輯：商品列表、購物車、結帳、訂單查詢（一律用 textContent，避免 XSS）
const $ = (sel) => document.querySelector(sel);
const money = (n) => `NT$ ${n.toLocaleString("zh-TW")}`;
const newCartId = () => `c_${crypto.randomUUID().replaceAll("-", "")}`;

function getCartId() {
  try {
    let id = localStorage.getItem("cartId");
    if (!id) {
      id = newCartId();
      localStorage.setItem("cartId", id);
    }
    return id;
  } catch {
    // 私密模式等情況 localStorage 不可用，改用本次頁面期間的暫時 id
    return newCartId();
  }
}
const cartId = getCartId();

let toastTimer;
function toast(message, isError = false) {
  const box = $("#toast");
  box.textContent = message;
  box.className = `toast show${isError ? " error" : ""}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    box.className = "toast";
  }, 2500);
}

async function api(path, options = {}) {
  let res;
  try {
    res = await fetch(path, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    throw new Error("無法連線到伺服器");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok)
    throw new Error(data.error?.message ?? `請求失敗（${res.status}）`);
  return data;
}

function el(tag, props = {}, children = []) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

// ---------- 商品 ----------
async function loadProducts() {
  const { products } = await api("/api/products");
  $("#productGrid").replaceChildren(
    ...products.map((p) => {
      const soldOut = p.stock <= 0;
      const btn = el("button", {
        className: "btn primary",
        textContent: soldOut ? "已售完" : "加入購物車",
        disabled: soldOut,
      });
      btn.addEventListener("click", () => addToCart(p.id, p.name));
      return el("article", { className: "card product" }, [
        el("div", { className: "emoji", textContent: p.emoji }),
        el("h3", { textContent: p.name }),
        el("p", { textContent: p.description }),
        el("span", { className: "price", textContent: money(p.price) }),
        el("span", { className: "stock", textContent: `庫存 ${p.stock}` }),
        btn,
      ]);
    }),
  );
}

async function addToCart(productId, name) {
  try {
    const { cart } = await api(`/api/cart/${cartId}/items`, {
      method: "POST",
      body: JSON.stringify({ productId, qty: 1 }),
    });
    renderCart(cart);
    toast(`已加入「${name}」`);
  } catch (err) {
    toast(err.message, true);
  }
}

// ---------- 購物車 ----------
function renderCart(cart) {
  $("#cartCount").textContent = cart.count;
  $("#cartTotal").textContent = money(cart.total);
  $("#checkoutForm").hidden = cart.items.length === 0;
  if (cart.items.length === 0) {
    $("#cartList").replaceChildren(
      el("li", { className: "empty", textContent: "購物車是空的，去逛逛吧！" }),
    );
    return;
  }
  $("#cartList").replaceChildren(
    ...cart.items.map((item) => {
      const minus = el("button", {
        className: "btn",
        textContent: "−",
        ariaLabel: "減少數量",
      });
      const plus = el("button", {
        className: "btn",
        textContent: "+",
        ariaLabel: "增加數量",
      });
      minus.addEventListener("click", () =>
        setQty(item.productId, item.qty - 1),
      );
      plus.addEventListener("click", () =>
        setQty(item.productId, item.qty + 1),
      );
      return el("li", { className: "card line" }, [
        el("span", { className: "emoji", textContent: item.emoji }),
        el("div", {}, [
          el("div", { textContent: item.name }),
          el("small", {
            className: "price",
            textContent: money(item.subtotal),
          }),
        ]),
        el("div", { className: "qty" }, [
          minus,
          el("span", { textContent: item.qty }),
          plus,
        ]),
      ]);
    }),
  );
}

async function loadCart() {
  const { cart } = await api(`/api/cart/${cartId}`);
  renderCart(cart);
}

async function setQty(productId, qty) {
  try {
    const { cart } = await api(`/api/cart/${cartId}/items/${productId}`, {
      method: "PATCH",
      body: JSON.stringify({ qty }),
    });
    renderCart(cart);
  } catch (err) {
    toast(err.message, true);
  }
}

$("#checkoutForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  if (!form.reportValidity()) return;
  const btn = form.querySelector("button");
  btn.disabled = true;
  try {
    const body = Object.fromEntries(new FormData(form));
    const { order } = await api("/api/checkout", {
      method: "POST",
      body: JSON.stringify({ cartId, ...body }),
    });
    toast(`訂單成立：${order.id}`);
    form.reset();
    await Promise.all([loadCart(), loadProducts()]);
    switchView("orders");
    renderOrders([order]);
  } catch (err) {
    toast(err.message, true);
  } finally {
    btn.disabled = false;
  }
});

// ---------- 訂單 ----------
function renderOrders(orders) {
  if (orders.length === 0) {
    $("#orderResult").replaceChildren(
      el("p", { className: "empty", textContent: "查無訂單" }),
    );
    return;
  }
  $("#orderResult").replaceChildren(
    ...orders.map((o) =>
      el("article", { className: "card order" }, [
        el("h3", { textContent: o.id }),
        el("small", {
          textContent: `${new Date(o.createdAt).toLocaleString("zh-TW")}・${o.status}・${o.customer.name}`,
        }),
        el(
          "ul",
          {},
          o.items.map((i) =>
            el("li", {
              textContent: `${i.name} × ${i.qty}　${money(i.subtotal)}`,
            }),
          ),
        ),
        el("b", { className: "price", textContent: `總計 ${money(o.total)}` }),
      ]),
    ),
  );
}

$("#orderForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = String(new FormData(e.currentTarget).get("q") ?? "").trim();
  try {
    if (/^09\d{8}$/.test(q)) {
      const { orders } = await api(
        `/api/orders?phone=${encodeURIComponent(q)}`,
      );
      renderOrders(orders);
    } else {
      const { order } = await api(`/api/orders/${encodeURIComponent(q)}`);
      renderOrders([order]);
    }
  } catch (err) {
    renderOrders([]);
    toast(err.message, true);
  }
});

// ---------- 分頁切換 ----------
function switchView(name) {
  document
    .querySelectorAll(".view")
    .forEach((v) => v.classList.toggle("active", v.id === `view-${name}`));
  document
    .querySelectorAll(".tabbar button")
    .forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  window.scrollTo(0, 0);
}
document
  .querySelectorAll(".tabbar button")
  .forEach((b) =>
    b.addEventListener("click", () => switchView(b.dataset.view)),
  );

Promise.all([loadProducts(), loadCart()]).catch((err) =>
  toast(err.message, true),
);
