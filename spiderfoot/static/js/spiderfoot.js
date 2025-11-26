//-------------------------------------------------------------------------------
// Name:         spiderfoot.js
// Purpose:      All the javascript code for the spiderfoot aspects of the UI.
//
// Author:      Steve Micallef <steve@binarypool.com>
//
// Created:     03/10/2012
// Copyright:   (c) Steve Micallef 2012
// Licence:     MIT
//-------------------------------------------------------------------------------

// Modern Theme Toggler using CSS Variables
document.addEventListener("DOMContentLoaded", () => {
  const themeToggler = document.getElementById("theme-toggler");
  const togglerText = document.getElementById("toggler-text");
  const htmlElement = document.documentElement;

  // Check for saved theme preference or default to 'light'
  const currentTheme = localStorage.getItem("theme") || "light";
  
  // Apply the theme on page load
  if (currentTheme === "dark") {
    htmlElement.setAttribute("data-theme", "dark");
    if (themeToggler) themeToggler.checked = true;
    if (togglerText) togglerText.innerText = "🌙 Dark";
  } else {
    htmlElement.removeAttribute("data-theme");
    if (themeToggler) themeToggler.checked = false;
    if (togglerText) togglerText.innerText = "☀️ Light";
  }

  // Theme toggle event listener
  if (themeToggler) {
    themeToggler.addEventListener("change", () => {
      if (themeToggler.checked) {
        // Switch to dark mode
        htmlElement.setAttribute("data-theme", "dark");
        localStorage.setItem("theme", "dark");
        if (togglerText) togglerText.innerText = "🌙 Dark";
      } else {
        // Switch to light mode
        htmlElement.removeAttribute("data-theme");
        localStorage.setItem("theme", "light");
        if (togglerText) togglerText.innerText = "☀️ Light";
      }
    });
  }
});

var sf = {};

sf.replace_sfurltag = function (data) {
  if (data.toLowerCase().indexOf("&lt;sfurl&gt;") >= 0) {
    data = data.replace(
      RegExp("&lt;sfurl&gt;(.*)&lt;/sfurl&gt;", "img"),
      "<a target=_new href='$1'>$1</a>"
    );
  }
  if (data.toLowerCase().indexOf("<sfurl>") >= 0) {
    data = data.replace(
      RegExp("<sfurl>(.*)</sfurl>", "img"),
      "<a target=_new href='$1'>$1</a>"
    );
  }
  return data;
};

sf.remove_sfurltag = function (data) {
  if (data.toLowerCase().indexOf("&lt;sfurl&gt;") >= 0) {
    data = data
      .toLowerCase()
      .replace("&lt;sfurl&gt;", "")
      .replace("&lt;/sfurl&gt;", "");
  }
  if (data.toLowerCase().indexOf("<sfurl>") >= 0) {
    data = data.toLowerCase().replace("<sfurl>", "").replace("</sfurl>", "");
  }
  return data;
};

sf.search = function (scan_id, value, type, postFunc) {
  sf.fetchData(
    docroot + "/search",
    { id: scan_id, eventType: type, value: value },
    postFunc
  );
};

sf.deleteScan = function(scan_id, callback) {
    var req = $.ajax({
      type: "GET",
      url: docroot + "/scandelete?id=" + scan_id
    });
    req.done(function() {
        alertify.success('<i class="glyphicon glyphicon-ok-circle"></i> <b>Scans Deleted</b><br/><br/>' + scan_id.replace(/,/g, "<br/>"));
        sf.log("Deleted scans: " + scan_id);
        callback();
    });
    req.fail(function (hr, textStatus, errorThrown) {
        alertify.error('<i class="glyphicon glyphicon-minus-sign"></i> <b>Error</b><br/></br>' + hr.responseText);
        sf.log("Error deleting scans: " + scan_id + ": " + hr.responseText);
    });
};

sf.stopScan = function(scan_id, callback) {
    var req = $.ajax({
      type: "GET",
      url: docroot + "/stopscan?id=" + scan_id
    });
    req.done(function() {
        alertify.success('<i class="glyphicon glyphicon-ok-circle"></i> <b>Scans Aborted</b><br/><br/>' + scan_id.replace(/,/g, "<br/>"));
        sf.log("Aborted scans: " + scan_id);
        callback();
    });
    req.fail(function (hr, textStatus, errorThrown) {
        alertify.error('<i class="glyphicon glyphicon-minus-sign"></i> <b>Error</b><br/><br/>' + hr.responseText);
        sf.log("Error stopping scans: " + scan_id + ": " + hr.responseText);
    });
};

sf.fetchData = function (url, postData, postFunc) {
  var req = $.ajax({
    type: "POST",
    url: url,
    data: postData,
    cache: false,
    dataType: "json",
  });

  req.done(postFunc);
  req.fail(function (hr, status) {
      alertify.error('<i class="glyphicon glyphicon-minus-sign"></i> <b>Error</b><br/>' + status);
  });
};

/*
sf.simpleTable = function(id, data, cols, linkcol=null, linkstring=null, sortable=true, rowfunc=null) {
	var table = "<table id='" + id + "' ";
	table += "class='table table-bordered table-striped tablesorter'>";
	table += "<thead><tr>";
	for (var i = 0; i < cols.length; i++) {
		table += "<th>" + cols[i] + "</th>";
	}
	table += "</tr></thead><tbody>";

	for (var i = 1; i < data.length; i++) {
		table += "<tr>";
		for (var c = 0; c < data[i].length; c++) {
			if (c == linkcol) {
				if (linkstring.indexOf("%%col") > 0) {
				}
				table += "<td>" + <a class='link' onClick='" + linkstring + "'>";
				table += data[i][c] + "</a></td>"
			} else {
				table += "<td>" + data[i][c] + "</td>";
			}
		}
		table += "</tr>";
	}
	table += "</tbody></table>";

	return table;
}

*/

sf.updateTooltips = function () {
  $(document).ready(function () {
    if ($("[rel=tooltip]").length) {
      $("[rel=tooltip]").tooltip({ container: "body" });
    }
  });
};

sf.log = function (message) {
  if (typeof console == "object" && typeof console.log == "function") {
    var currentdate = new Date();
    var pad = function (n) {
      return ("0" + n).slice(-2);
    };
    var datetime =
      currentdate.getFullYear() +
      "-" +
      pad(currentdate.getMonth() + 1) +
      "-" +
      pad(currentdate.getDate()) +
      " " +
      pad(currentdate.getHours()) +
      ":" +
      pad(currentdate.getMinutes()) +
      ":" +
      pad(currentdate.getSeconds());
    console.log("[" + datetime + "] " + message);
  }
};

// Modern download helper function
sf.downloadFile = function(url, logMessage) {
  if (logMessage) {
    sf.log(logMessage);
  }
  
  // Create a temporary link element
  var link = document.createElement('a');
  link.href = url;
  link.style.display = 'none';
  
  // Add to document, click, and remove
  document.body.appendChild(link);
  link.click();
  
  // Clean up after a short delay
  setTimeout(function() {
    document.body.removeChild(link);
  }, 100);
};
