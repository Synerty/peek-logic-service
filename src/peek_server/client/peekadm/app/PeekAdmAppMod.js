'use strict';

// --------------------- Angular Application----------------------------

var peekAdmConfigDashboardPath = '/peekadm';
var peekAdmConfigSettingPath = '/peekadm/setting';
var peekAdmConfigUpdatePath = '/peekadm/update';
var peekAdmConfigCoordSetPath = '/peekadm/coordset';

define([
            // Main app requirements
            "angular", "jquery", "bootstrap",
            // Angular mod requirements
            "angular-route", "angular-bootstrap",
            // Admin interface modules
            "PeekAdmUpdateMod", "PeekAdmSettingMod", "PeekAdmNavbarMod",
            "PeekAdmDashboardMod"
        ],
        function () {


            var peekAdmAppCtrlMod = angular.module('peekAdmAppCtrlMod', []);

            var peekAdminApp = angular.module('peekAdminApp', ['rapuiMod', 'ngRoute',
                'ui.bootstrap',
                'peekAdmAppCtrlMod', 'peekAdmDashboardMod', 'peekAdmNavbarMod',
                'peekAdmUpdateMod', 'peekAdmSettingMod']);

            // --------------------- Angular Application----------------------------

            // Bind angular to the document, the ng-app directive
            $(function () {
                angular.bootstrap(document, ["peekAdminApp"]);
            });

            // --------------------- Angular Application----------------------------

            peekAdminApp.run(function ($rootScope) {
                $rootScope.peekAdmConfigDashboardPath = peekAdmConfigDashboardPath;
                $rootScope.peekAdmConfigSettingPath = peekAdmConfigSettingPath;
                $rootScope.peekAdmConfigUpdatePath = peekAdmConfigUpdatePath;
                $rootScope.peekAdmConfigCoordSetPath = peekAdmConfigCoordSetPath;
            });


            var peekAdmDashboardRoute = {
                templateUrl: 'view/PeekAdmDashboard.html',
                caseInsensitiveMatch: true
            };

            var peekAdmSettingRoute = {
                templateUrl: 'view/PeekAdmSetting.html',
                caseInsensitiveMatch: true
            };

            var peekAdmUpdateRoute = {
                templateUrl: 'view/PeekAdmUpdate.html',
                caseInsensitiveMatch: true
            };

            var peekAdmCoordSetRoute = {
                templateUrl: 'view/PeekAdmCoordSet.html',
                caseInsensitiveMatch: true
            };

            // Add in our admin routes, The main application configures the rest
            peekAdminApp.config(['$routeProvider', '$locationProvider',
                function ($routeProvider, $locationProvider) {
                    $locationProvider.html5Mode(true);

                    $routeProvider
                            .when(peekAdmConfigDashboardPath, peekAdmDashboardRoute)
                            .when(peekAdmConfigSettingPath, peekAdmSettingRoute)
                            .when(peekAdmConfigUpdatePath, peekAdmUpdateRoute)
                            .when(peekAdmConfigCoordSetPath, peekAdmCoordSetRoute)
                            .otherwise({
                                redirectTo: peekAdmConfigDashboardPath
                            })
                    ;

                }]);

// ------ PeekRootCtrl
            peekAdminApp.controller('PeekAdmAppCtrl', ['$scope', function ($scope) {

            }]);

        }
);

