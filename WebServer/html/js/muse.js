window.Muse.assets.check = function (d) {
    if (!window.Muse.assets.checked) {
        window.Muse.assets.checked = !0;
        var b = {}, c = function (a, b) {
            if (window.getComputedStyle) {
                var c = window.getComputedStyle(a, null);
                return c && c.getPropertyValue(b) || c && c[b] || ""
            }
            if (document.documentElement.currentStyle) return (c = a.currentStyle) && c[b] || a.style && a.style[b] || "";
            return ""
        }, a = function (a) {
            if (a.match(/^rgb/)) return a = a.replace(/\s+/g, "").match(/([\d\,]+)/gi)[0].split(","), (parseInt(a[0]) << 16) + (parseInt(a[1]) << 8) + parseInt(a[2]);
            if (a.match(/^\#/)) return parseInt(a.substr(1),
                16);
            return 0
        }, g = function (g) {
            for (var f = document.getElementsByTagName("link"), h = 0; h < f.length; h++) if ("text/css" == f[h].type) {
                var i = (f[h].href || "").match(/\/?css\/([\w\-]+\.css)\?crc=(\d+)/);
                if (!i || !i[1] || !i[2]) break;
                b[i[1]] = i[2]
            }
            f = document.createElement("div");
            f.className = "version";
            f.style.cssText = "display:none; width:1px; height:1px;";
            document.getElementsByTagName("body")[0].appendChild(f);
            for (h = 0; h < Muse.assets.required.length;) {
                var i = Muse.assets.required[h], l = i.match(/([\w\-\.]+)\.(\w+)$/), k = l && l[1] ?
                    l[1] : null, l = l && l[2] ? l[2] : null;
                switch (l.toLowerCase()) {
                    case "css":
                        k = k.replace(/\W/gi, "_").replace(/^([^a-z])/gi, "_$1");
                        f.className += " " + k;
                        k = a(c(f, "color"));
                        l = a(c(f, "backgroundColor"));
                        k != 0 || l != 0 ? (Muse.assets.required.splice(h, 1), "undefined" != typeof b[i] && (k != b[i] >>> 24 || l != (b[i] & 16777215)) && Muse.assets.outOfDate.push(i)) : h++;
                        f.className = "version";
                        break;
                    case "js":
                        h++;
                        break;
                    default:
                        throw Error("Unsupported file type: " + l);
                }
            }
            d ? d().jquery != "1.8.3" && Muse.assets.outOfDate.push("jquery-1.8.3.min.js") : Muse.assets.required.push("jquery-1.8.3.min.js");
            f.parentNode.removeChild(f);
            if (Muse.assets.outOfDate.length || Muse.assets.required.length) f = "서버의 일부 파일이 누락되었거나 올바르지 않습니다. 브라우저 캐시를 지우고 다시 시도하십시오. 문제가 지속되면 웹사이트 작성자에게 문의하십시오.", g && Muse.assets.outOfDate.length && (f += "\nOut of date: " + Muse.assets.outOfDate.join(",")), g && Muse.assets.required.length && (f += "\nMissing: " + Muse.assets.required.join(",")), suppressMissingFileError ? (f += "\nUse SuppressMissingFileError key in AppPrefs.xml to show missing file error pop up.", console.log(f)) : alert(f)
        };
        location && location.search && location.search.match && location.search.match(/muse_debug/gi) ?
            setTimeout(function () {
                g(!0)
            }, 5E3) : g()
    }
};
var muse_init = function () {
    require.config({baseUrl: ""});
    require(["jquery", "museutils", "whatinput", "jquery.watch"], function (d) {
        var $ = d;
        $(document).ready(function () {
            try {
                window.Muse.assets.check($);
                /* body */
                Muse.Utils.transformMarkupToFixBrowserProblemsPreInit();
                /* body */
                Muse.Utils.prepHyperlinks(true);
                /* body */
                Muse.Utils.makeButtonsVisibleAfterSettingMinWidth();
                /* body */
                Muse.Utils.fullPage('#page');
                /* 100% height page */
                Muse.Utils.showWidgetsWhenReady();
                /* body */
                Muse.Utils.transformMarkupToFixBrowserProblems();
                /* body */
            } catch (b) {
                if (b && "function" == typeof b.notify ? b.notify() : Muse.Assert.fail("Error calling selector function: " + b), false) throw b;
            }
        })
    })
};