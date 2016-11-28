
import * as angular from "angular";
import * as $ from "jquery";
import "angular-ui-bootstrap";
import "angular-route";

import {logInfo} from "../../../../../txhttputil/txhttputil/usr_msg_dispatcher/UsrMsgDispatcher";
import AngFormLoadController from "../../../../../txhttputil/txhttputil/angular_custom/AngFormLoadController";





// -------------------------- Dashboard Module -----------------------
let peekDashboardMod = angular.module("peekAdmDashboardMod", []);


// ------ PeekDashboardCtrl
peekDashboardMod.controller("PeekAdmDashboardCtrl", [
    "$scope",
    "$location",
    function ($scope, $location) {
        let self = this;


    }]);

// ------------- The list controller for this page
peekDashboardMod.controller("PeekAdmDashboardListCtrl", [
    "$scope",
    function ($scope) {
        let self = this;

        self.loader = new AngFormLoadController($scope,
            {
                papp: "platform",
                key: "peakadm.dashboard.list.data"
            }, {
                objName: "dashboardList",
                dataIsArray: true,
                actionPostfix: "Stats"
            });

        self.loader.loadCallback.add(function () {
            logInfo("Dashboard Refreshed")
        });


    }]);

// Add custom directive for peek_server-execute-list
peekDashboardMod.directive("peekAdmDashboardList", function () {
    return {
        restrict: "E",
        templateUrl: "/view/PeekAdmDashboardList.html"
    };
});

