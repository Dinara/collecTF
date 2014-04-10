/*global $,document,window*/
"use strict";
if (!window.console) {
    window.console = {};
}
if (!window.console.log) {
    window.console.log = function () { };
}

function get_wiki(name) {
    // given title, return first paragraph of wikipedia article
    $.ajax({
        url: 'http://en.wikipedia.org/w/api.php',
        data: {
            action: 'parse',
            //titles: name,
            page: name,
            format: 'json',
            prop: 'text',
        },
        dataType: 'jsonp',
        success: function (data) {
            var wikiDOM = $("<document>" + data.parse.text['*'] + "</document>");
            var first_p = $(wikiDOM.children('p').get(0));

            first_p.find('sup').remove();
            first_p.find('a').each(function () {
                $(this)
                    .attr('href', 'http://en.wikipedia.org' + $(this).attr('href'))
                    .attr('target', 'wikipedia');
            });
            //console.log($(first_p));
            var desc = $('#description');
            desc.text('');
            desc.append('<h4>' + name + '</h4>');
            desc.append(first_p)
                .append("<a href='http://en.wikipedia.org/wiki/" +
                        name +
                        "' target='wikipedia'>Read more on Wikipedia</a>");
        }
    });
}

function getReportLinksSpecies(id) {
    // retrieve list of reports
    $(document).ajaxStop($.unblockUI); // unblock when ajax activity stops
    $.blockUI();
    $.ajax({
        type: "GET",
        url: '/browse/get_results_tax/' + id,
        success: function (data) {
            $("#browse").html(data);
            get_wiki($("#browse #description h4").text());
        }
    });
}

function getReportLinksTechniques(type, id) {
    // retrieve list of reports
    $(document).ajaxStop($.unblockUI); // unblock when ajax activity stops
    $.blockUI();
    $.ajax({
        type: "GET",
        url: '/browse/get_results_tech/' + type + '/' + id,
        success: function (data) {
            $("#browse").html(data);
        }
    });
}

function getReportLinksTF(type, id) {
    // Given string type (TF_family|TF) and id of the object, perform ajax to
    // retrieve list of reports
    $(document).ajaxStop($.unblockUI); // unblock when ajax activity stops
    $.blockUI();
    $.ajax({
        type: "GET",
        url: '/browse/get_results_tf/' + type + '/' + id,
        success: function (data) {
            $("#browse").html(data);
        }
    });
}

$(document).ready(function () {

});
