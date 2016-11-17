'use strict';

// --------------------- Angular Application----------------------------

var peekAdmConfigDashboardPath = '/';
var peekAdmConfigSettingPath = '/setting';
var peekAdmConfigUpdatePath = '/update';
var peekAdmConfigEnvPath = '/env';

import { AngFormLoadController } from "AngFormLoadController";
import { angular } from "angular";
import { AngFormLoadController } from "AngFormLoadController";
import { AngFormLoadController } from "AngFormLoadController";
import { AngFormLoadController } from "AngFormLoadController";
import { AngFormLoadController } from "AngFormLoadController";

define([
            // Named dependencies
            "AngFormLoadController",
            // Main app requirements
            "angular", "jquery", "bootstrap",
            // Angular mod requirements
            "angular-route", "angular-bootstrap",
            // Admin interface modules
            "PeekAdmUpdateMod", "PeekAdmSettingMod", "PeekAdmNavbarMod",
            "PeekAdmDashboardMod", "PeekAdmEnvMod"
        ],
        function (AngFormLoadController) {


            var peekAdmAppCtrlMod = angular.module('peekAdmAppCtrlMod', []);

            var peekAdminApp = angular.module('peekAdminApp', ['rapuiMod', 'ngRoute',
                'ui.bootstrap',
                'peekAdmAppCtrlMod', 'peekAdmDashboardMod', 'peekAdmNavbarMod',
                'peekAdmUpdateMod', 'peekAdmSettingMod',
                'peekAdmEnvMod'
            ]);

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
                $rootScope.peekAdmConfigEnvPath = peekAdmConfigEnvPath;
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

            var peekAdmEnvRoute = {
                templateUrl: 'view/PeekAdmEnv.html',
                caseInsensitiveMatch: true
            };

            // Add in our admin routes, The main application configures the rest
            peekAdminApp.config(['$routeProvider', '$locationProvider',

                function ($routeProvider, $locationProvider) {
                    var self = this;

                    var $scope = {
                        pappsMenuData : [],
                        $on: function () {
                        }
                    };

                    $locationProvider.html5Mode(true);

                    $routeProvider
                            .when(peekAdmConfigDashboardPath, peekAdmDashboardRoute)
                            .when(peekAdmConfigSettingPath, peekAdmSettingRoute)
                            .when(peekAdmConfigUpdatePath, peekAdmUpdateRoute)
                            .when(peekAdmConfigEnvPath, peekAdmEnvRoute)
                            .otherwise({
                                redirectTo: peekAdmConfigDashboardPath
                            })
                    ;


                    var loader = new AngFormLoadController($scope,
                            {
                                papp: "peek_server",
                                key: "nav.adm.papp.list"
                            }, {
                                loadOnInit: false,
                                objName: 'pappsMenuData',
                                dataIsArray: true
                            });


                    loader.loadCallback.add(function () {
                        // For simplicity's sake we assume that:
                        //  1. `path` has no trailing `/`
                        //  2. the route associated with `path` has a `templateUrl`
                        //  3. everything exists, so we don't check for empty values
                        // function removeRoute(path) {
                        //     var route1 = $route.routes[path];
                        //     var route2 = $route.routes[path + '/'];
                        //     var tmplUrl = $route.routes[path].templateUrl;
                        //
                        //     $templateCache.remove(tmplUrl);
                        //     delete $route.routes[path];
                        //     delete $route.routes[path + '/'];
                        // }
                        //
                        // var routeNames = dictKeysFromObject($route.routes);
                        var i;
                        //
                        // // Remove existing PAPP routes
                        // for (i = 0; i < routeNames.length; i++) {
                        //     var routePath = routeNames[i];
                        //     var lastChar = routePath[routePath.length - 1];
                        //     if (routePath.indexOf("/papp_") == 0 && lastChar != '/') {
                        //         removeRoute(routePath);
                        //     }
                        //
                        // }

                        for (i = 0; i < $scope.pappsMenuData.length; i++) {
                            var pappMenu = $scope.pappsMenuData[i];
                            $routeProvider.when(pappMenu.url, {
                                templateUrl: pappMenu.templateUrl,
                                caseInsensitiveMatch: true
                            });
                        }

                    });


                }]);

// ------ PeekRootCtrl
            peekAdminApp.controller('PeekAdmAppCtrl', ['$scope', function ($scope) {

            }]);

        }
);

