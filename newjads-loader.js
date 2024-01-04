var files = [
  "newjads-001.txt",
  "newjads-002.txt",
  "newjads-003.txt",
  "newjads-004.txt",
  "newjads-005.txt",
  "newjads-006.txt",
  "newjads-007.txt",
  "newjads-008.txt",
  "newjads-009.txt",
  "newjads-010.txt",
  "newjads-011.txt",
  "newjads-012.txt"
];

var data = "";

for (let i = 0; i < files.length; i++) {
  let file = files[i];
  let rawFile = new XMLHttpRequest();
  rawFile.open("GET", file, false);
  rawFile.onreadystatechange = function () {
    if (rawFile.readyState === 4) {
      if (rawFile.status === 200 || rawFile.status == 0) {
        data += rawFile.responseText;
      }
    }
  };
  rawFile.send(null);
}

var data_script = document.getElementById("data");
data_script.innerHTML = data;