var list_el = [];

function check_duplicates() {
  els = document.getElementsByClassName("nested");
  for (el in els) {
    var text = el.textContent;
    list_el.push(text);

    if(list_el.includes(text)){
      el.classList.add("repeated");
    }

  }
}