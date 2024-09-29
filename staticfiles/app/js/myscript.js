$(".plus-cart").click(function () {
  var pid = $(this).attr("pid").toString();
  var quan = this.parentNode.children[2];
  console.log("pid: ", pid);
  $.ajax({
    type: "GET",
    url: "/pluscart",
    data: {
      prod_id: pid,
    },
    success: function (data) {
      console.log("Data - ", data);
      quan.innerText = data.quantity;
      document.getElementById("amount").innerText = data.amount;
      document.getElementById("totalamount").innerText = data.totalamount;
    },
  });
});

$(".minus-cart").click(function () {
  var pid = $(this).attr("pid").toString();
  var quan = this.parentNode.children[2];
  $.ajax({
    type: "GET",
    url: "/minuscart",
    data: {
      prod_id: pid,
    },
    success: function (data) {
      console.log(data);
      quan.innerText = data.quantity;
      document.getElementById("amount").innerText = data.amount;
      document.getElementById("totalamount").innerText = data.totalamount;
    },
  });
});

$(".remove-cart").click(function () {
  var pid = $(this).attr("pid").toString();
  var node = this;
  $.ajax({
    type: "GET",
    url: "/removeitem",
    data: {
      prod_id: pid,
    },
    success: function (data) {
      document.getElementById("amount").innerText = data.amount;
      document.getElementById("totalamount").innerText = data.totalamount;
      node.parentNode.parentNode.parentNode.parentNode.remove();
    },
  });
});
