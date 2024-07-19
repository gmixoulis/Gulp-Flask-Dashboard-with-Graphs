import { initNavbar } from './navbar/navbar';
import { initHero } from './hero/hero';
import { initTabs } from './tabs/tabs';
import { initCountdown } from './countdown/countdown';
import { initRoadmap } from './roadmap/roadmap';
import { initLike } from './like/like';
import { initBackToTop } from './backtotop/backtotop';

window.initNavbar = initNavbar;
window.initHero = initHero;
window.initTabs = initTabs;
window.initCountdown = initCountdown;
window.initRoadmap = initRoadmap;
window.initLike = initLike;
window.initBackToTop = initBackToTop;



renderjson.set_property_list(void 0)
              .set_replacer(function(k,v) {
        var obj_from_dom = function (el) {
            if (el.nodeType == el.TEXT_NODE)
                return el.data;
            var attributes="";
            if (el.attributes)
                for (var i=0; i<el.attributes.length; i++)
                    attributes += " "+el.attributes.item(i).name + "=\"" + el.attributes.item(i).value + "\"";
            var obj = {};
            obj["<"+el.tagName+attributes+">"] = Array.prototype.map.call(el.childNodes, obj_from_dom);
            return obj;
        };
        if (v === window) return "<window>";
        if (v === document) return "<document>";
        if (typeof(v) == "number") return isFinite(v) ? v : v.toString(); // Capture NaNs and Infinity
        if (typeof(v) == "object" && v && "nodeType" in v) return obj_from_dom(v);
        else return v;
    });
