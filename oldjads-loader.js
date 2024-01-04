var files = [
  "oldjads-001.txt",
  "oldjads-002.txt",
  "oldjads-003.txt",
  "oldjads-004.txt",
  "oldjads-005.txt",
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