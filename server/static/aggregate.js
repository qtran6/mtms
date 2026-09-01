const $ = id => document.getElementById(id);
const today = () => new Date().toISOString().slice(0, 10);
const fmt = n => n.toLocaleString("vi-VN");

let items = [];   // in-memory edits live here

async function load() {
  const params = new URLSearchParams({
    date_from: $("date-from").value,
    date_to: $("date-to").value,
  });
  const data = await fetch("/api/aggregate?" + params).then(r => r.json());
  items = data.items;
  render();
}

function render() {
  const body = $("body");
  if (!items.length) {
    body.innerHTML = '<div class="empty">Chưa có đơn hàng trong khoảng ngày này.</div>';
    return;
  }
  const rows = items.map((it, i) => `
    <tr>
      <td class="muted">${it.brand || "—"}</td>
      <td>${it.name}</td>
      <td class="num"><input type="number" min="0" step="1" value="${it.qty}"
                              data-i="${i}" data-field="qty" class="edit"></td>
      <td class="num"><input type="number" min="0" step="1000" value="${it.price}"
                              data-i="${i}" data-field="price" class="edit"></td>
      <td class="num" id="total-${i}">${fmt(it.total)}</td>
    </tr>`).join("");

  body.innerHTML = `
    <table>
      <thead><tr>
        <th style="width: 100px;">Thương hiệu</th>
        <th>Tên</th>
        <th class="num" style="width: 80px;">SL</th>
        <th class="num" style="width: 130px;">Đơn giá</th>
        <th class="num" style="width: 140px;">Thành tiền</th>
      </tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr>
        <td colspan="4" style="text-align: right; font-weight: 500;">Tổng cộng</td>
        <td class="num" style="font-weight: 500; font-size: 14px;" id="grand">${fmt(grandTotal())}</td>
      </tr></tfoot>
    </table>`;

  body.querySelectorAll("input.edit").forEach(el => {
    el.addEventListener("input", onEdit);
  });
}

function onEdit(e) {
  const i = +e.target.dataset.i;
  const field = e.target.dataset.field;
  const val = parseFloat(e.target.value) || 0;
  items[i][field] = val;
  items[i].total = items[i].qty * items[i].price;
  $("total-" + i).textContent = fmt(items[i].total);
  $("grand").textContent = fmt(grandTotal());
}

function grandTotal() {
  return items.reduce((sum, it) => sum + it.total, 0);
}

$("date-from").value = today();
$("date-to").value = today();
["date-from", "date-to"].forEach(id => $(id).addEventListener("change", load));

load();