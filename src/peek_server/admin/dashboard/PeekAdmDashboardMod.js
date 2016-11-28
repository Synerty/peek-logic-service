"use strict";
var angular = require("angular");
require("angular-ui-bootstrap");
require("angular-route");
var UsrMsgDispatcher_1 = require("../../../../../txwebutil/txwebutil/usr_msg_dispatcher/UsrMsgDispatcher");
var AngFormLoadController_1 = require("../../../../../txwebutil/txwebutil/angular_custom/AngFormLoadController");
// -------------------------- Dashboard Module -----------------------
var peekDashboardMod = angular.module("peekAdmDashboardMod", []);
// ------ PeekDashboardCtrl
peekDashboardMod.controller("PeekAdmDashboardCtrl", [
    "$scope",
    "$location",
    function ($scope, $location) {
        var self = this;
    }]);
// ------------- The list controller for this page
peekDashboardMod.controller("PeekAdmDashboardListCtrl", [
    "$scope",
    function ($scope) {
        var self = this;
        self.loader = new AngFormLoadController_1.default($scope, {
            papp: "platform",
            key: "peakadm.dashboard.list.data"
        }, {
            objName: "dashboardList",
            dataIsArray: true,
            actionPostfix: "Stats"
        });
        self.loader.loadCallback.add(function () {
            UsrMsgDispatcher_1.logInfo("Dashboard Refreshed");
        });
    }]);
// Add custom directive for peek_server-execute-list
peekDashboardMod.directive("peekAdmDashboardList", function () {
    return {
        restrict: "E",
        templateUrl: "/view/PeekAdmDashboardList.html"
    };
});
//# sourceMappingURL=PeekAdmDashboardMod.js.map