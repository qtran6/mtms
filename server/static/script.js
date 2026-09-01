const $ = id => document.getElementById(id);
const today = () => new Date().toISOString().slice(0, 10);
const fmt = n => n.toLocaleString("vi-VN");

async function loadOptions() {
  const [brands, clients] = await Promise.all([
    fetch("/brands").then(r => r.json()),
    fetch("/clients").then(r => r.json()),
  ]);
  $("brand").innerHTML = '<option value="">Tất cả</option>' +
    brands.map(b => `<option>${b}</option>`).join("");
  $("client").innerHTML = '<option value="">Tất cả</option>' +
    clients.map(c => `<option>${c}</option>`).join("");
}

async function load() {
  const d = $("date").value;
  $("date-label").textContent = new Date(d).toLocaleDateString("vi-VN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  });

  const params = new URLSearchParams({ date: d });
  if ($("brand").value)    params.set("brand",    $("brand").value);
  if ($("client").value)   params.set("client",   $("client").value);
  if ($("customer").value) params.set("customer", $("customer").value);

  const orders = await fetch("/orders?" + params).then(r => r.json());
  render(orders);
}

function render(orders) {
  const body = $("body");
  if (!orders.length) {
    body.innerHTML = '<div class="empty">Chưa có đơn hàng nào.</div>';
    return;
  }
  const rows = orders.map(o => {
    const time = o.printed_at.slice(11, 16);
    const items = o.rows.map(r => `
      <tr>
        <td>${r.name}</td>
        <td class="num">${r.qty}</td>
        <td class="num">${fmt(r.price)}</td>
        <td class="num">${fmt(r.total)}</td>
      </tr>`).join("");
    return `
      <tr class="order" onclick="toggle(${o.id})">
        <td>${time}</td>
        <td class="muted">${o.client_name}</td>
        <td>${o.customer || ""}</td>
        <td class="num">${o.rows.length}</td>
        <td class="del" onclick="event.stopPropagation(); del(${o.id})" title="Xóa">🗑</td>
      </tr>
      <tr id="detail-${o.id}" class="detail" style="display: none;">
        <td colspan="5">
          <table>
            <tr class="muted">
              <td>Tên HH</td>
              <td class="num">SL</td>
              <td class="num">Đơn giá</td>
              <td class="num">Thành tiền</td>
            </tr>
            ${items}
          </table>
        </td>
      </tr>`;
  }).join("");

  body.innerHTML = `
    <table>
      <thead><tr>
        <th style="width: 70px;">Giờ</th>
        <th style="width: 80px;">Máy</th>
        <th>Khách hàng</th>
        <th class="num" style="width: 60px;">SL</th>
        <th style="width: 40px;"></th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

async function del(id) {
  if (!confirm("Xóa đơn hàng này?")) return;
  const res = await fetch("/orders/" + id, { method: "DELETE" });
  if (res.ok) {
    load();
  } else {
    alert("Không xóa được. Vui lòng thử lại.");
  }
}

function toggle(id) {
  const el = $("detail-" + id);
  el.style.display = el.style.display === "none" ? "" : "none";
}

function shiftDay(delta) {
  const d = new Date($("date").value);
  d.setDate(d.getDate() + delta);
  $("date").value = d.toISOString().slice(0, 10);
  load();
}

$("date").value = today();
["date", "brand", "client"].forEach(id => $(id).addEventListener("change", load));

let debounce;
$("customer").addEventListener("input", () => {
  clearTimeout(debounce);
  debounce = setTimeout(load, 200);
});

loadOptions().then(load);