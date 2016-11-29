/// <amd-dependency path="angular"/>
'use strict';
define([
    // Named Depencencies
    "AngFormLoadController",
    // Unnamed Dependencies
    "angular", "jquery"
], function (AngFormLoadController) {
    // -------------------------- Env Module -----------------------
    var peekAdmEnvMod = angular.module('peekAdmEnvMod', []);
    // ------ PeekEnvCtrl
    peekAdmEnvMod.controller('PeekAdmEnvCtrl', [
        '$scope',
        '$location',
        function ($scope, $location) {
            var self = this;
        }]);
    // ------------- The list controller for this page
    peekAdmEnvMod.controller('PeekAdmEnvServerListCtrl', [
        '$scope',
        function ($scope) {
            var self = this;
            self.loader = new AngFormLoadController($scope, { key: "peakadm.env.server.list.data" }, {
                objName: 'servers',
                dataIsArray: true,
                actionPostfix: 'Servers'
            });
        }]);
    // Add custom directive for peek_server_be-execute-list
    peekAdmEnvMod.directive('peekAdmEnvServerList', function () {
        return {
            restrict: 'E',
            templateUrl: '/view/PeekAdmEnvServerList.html'
        };
    });
    // ------------- The list controller for this page
    peekAdmEnvMod.controller('PeekAdmEnvAgentListCtrl', [
        '$scope',
        function ($scope) {
            var self = this;
            self.loader = new AngFormLoadController($scope, { key: "peakadm.env.platform.list.data" }, {
                objName: 'agents',
                dataIsArray: true,
                actionPostfix: 'Agents'
            });
        }]);
    // Add custom directive for peek_server_be-execute-list
    peekAdmEnvMod.directive('peekAdmEnvAgentList', function () {
        return {
            restrict: 'E',
            templateUrl: '/view/PeekAdmEnvAgentList.html'
        };
    });
    // ------------- The list controller for this page
    peekAdmEnvMod.controller('PeekAdmEnvWorkerListCtrl', [
        '$scope',
        function ($scope) {
            var self = this;
            self.loader = new AngFormLoadController($scope, { key: "peakadm.env.worker.list.data" }, {
                objName: 'workers',
                dataIsArray: true,
                actionPostfix: 'Workers'
            });
        }]);
    // Add custom directive for peek_server_be-execute-list
    peekAdmEnvMod.directive('peekAdmEnvWorkerList', function () {
        return {
            restrict: 'E',
            templateUrl: '/view/PeekAdmEnvWorkerList.html'
        };
    });
});
//# sourceMappingURL=PeekAdmEnvMod.js.map