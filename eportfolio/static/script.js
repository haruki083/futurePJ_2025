// script.js（CSPに対応するため、インラインJavaScriptは使わずこのファイルにまとめる）
document.addEventListener("DOMContentLoaded", function () {
  // 削除などの確認ダイアログ
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // 二重送信防止：送信したらボタンを一時的に無効化する
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (e.defaultPrevented) return;
      if (form.dataset.submitting === "1") {
        e.preventDefault();
        return;
      }
      form.dataset.submitting = "1";
      form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (btn) {
        btn.disabled = true;
      });
      setTimeout(function () {
        form.dataset.submitting = "0";
        form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (btn) {
          btn.disabled = false;
        });
      }, 10000);
    });
  });

  // 記録フォーム：種類が「出席」のときだけ出欠欄を表示
  var category = document.getElementById("category");
  var attendance = document.getElementById("attendance-field");
  if (category && attendance) {
    var toggle = function () {
      attendance.classList.toggle("d-none", category.value !== "attendance");
    };
    category.addEventListener("change", toggle);
    toggle();
  }
});
