/// <amd-dependency path="angular"/>
'use strict';

define([
            // Named Depencencies
            "AngFormLoadController",
            // Unnamed Dependencies
            "angular", "jquery"
        ], function (AngFormLoadController) {
// -------------------------- Dashboard Module -----------------------
            var peekDashboardMod = angular.module('peekAdmDashboardMod', []);


// ------ PeekDashboardCtrl
            peekDashboardMod.controller('PeekAdmDashboardCtrl', [
                '$scope',
                '$location',
                function ($scope, $location) {
                    var self = this;


                }]);

// ------------- The list controller for this page
            peekDashboardMod.controller('PeekAdmDashboardListCtrl', [
                '$scope',
                function ($scope) {
                    var self = this;

                    self.loader = new AngFormLoadController($scope,
                            {
                                papp: 'platform',
                                key: "peakadm.dashboard.list.data"
                            }, {
                                objName: 'dashboardList',
                                dataIsArray: true,
                                actionPostfix: 'Stats'
                            });

                    self.loader.loadCallback.add(function () {
                        logInfo("Dashboard Refreshed")
                    });


                }]);

// Add custom directive for peek_server-execute-list
            peekDashboardMod.directive('peekAdmDashboardList', function () {
                return {
                    restrict: 'E',
                    templateUrl: '/view/PeekAdmDashboardList.html'
                };
            });


        }
);