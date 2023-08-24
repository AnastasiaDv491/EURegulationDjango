var elements = document.querySelectorAll('.document_name');
var arrayOfUsedNames = [];

for (var i = 0; i < elements.length; i++)
{
  var index = arrayOfUsedNames.indexOf(elements[i].innerHTML);

  if (index == -1)
  {
    arrayOfUsedNames.push(elements[i].innerHTML);
  } 

  else
  {
    elements[i].classList.add("repeated")
  }

}

console.log(arrayOfUsedNames);