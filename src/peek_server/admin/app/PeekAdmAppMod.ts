import "txhttputil";

import * as angular from "angular";
import * as $ from "jquery";
import "angular-ui-bootstrap";
import "angular-route";

// Import angular modules
import "PeekAdmUpdateMod";
import "PeekAdmSettingMod";
import "PeekAdmNavbarMod";
import "PeekAdmDashboardMod";
import "PeekAdmEnvMod";
import AngFormLoadController from "../../../../../txhttputil/txhttputil/angular_custom/AngFormLoadController";
//
// define([
//         // Named dependencies
//         "AngFormLoadController",
//         // Main app requirements
//         "angular", "jquery", "bootstrap",
//         // Angular mod requirements
//         "angular-route", "angular-bootstrap",
//         // Admin interface modules
//         "PeekAdmUpdateMod", "PeekAdmSettingMod", "PeekAdmNavbarMod",
//         "PeekAdmDashboardMod", "PeekAdmEnvMod"
//     ],
//     function (AngFormLoadController) {
//
//     }
// );

// --------------------- Angular Application----------------------------

let peekAdmConfigDashboardPath = "/";
let peekAdmConfigSettingPath = "/setting";
let peekAdmConfigUpdatePath = "/update";
let peekAdmConfigEnvPath = "/env";

let peekAdmAppCtrlMod = angular.module("peekAdmAppCtrlMod", []);

let peekAdminApp = angular.module("peekAdminApp", ["rapuiMod", "ngRoute",
    "ui.bootstrap",
    "peekAdmAppCtrlMod", "peekAdmDashboardMod", "peekAdmNavbarMod",
    "peekAdmUpdateMod", "peekAdmSettingMod",
    "peekAdmEnvMod"
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


let peekAdmDashboardRoute = {
    templateUrl: "view/PeekAdmDashboard.html",
    caseInsensitiveMatch: true
};

let peekAdmSettingRoute = {
    templateUrl: "view/PeekAdmSetting.html",
    caseInsensitiveMatch: true
};

let peekAdmUpdateRoute = {
    templateUrl: "view/PeekAdmUpdate.html",
    caseInsensitiveMatch: true
};

let peekAdmEnvRoute = {
    templateUrl: "view/PeekAdmEnv.html",
    caseInsensitiveMatch: true
};


export interface IAutoLoad extends angular.IScope {
    _startApplying: boolean;
}

// Add in our admin routes, The main application configures the rest
peekAdminApp.config(["$routeProvider", "$locationProvider",

    function ($routeProvider, $locationProvider) {
        let self = this;

        let $scope = new angular.IScope();
        $scope["pappsMenuData"] =  [];

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


        let loader = new AngFormLoadController($scope,
            {
                papp: "peek_server",
                key: "nav.adm.papp.list"
            }, {
                loadOnInit: false,
                objName: "pappsMenuData",
                dataIsArray: true
            });


        loader.loadCallback.add(function () {
            // For simplicity's sake we assume that:
            //  1. `path` has no trailing `/`
            //  2. the route associated with `path` has a `templateUrl`
            //  3. everything exists, so we don't check for empty values
            // function removeRoute(path) {
            //     let route1 = $route.routes[path];
            //     let route2 = $route.routes[path + "/"];
            //     let tmplUrl = $route.routes[path].templateUrl;
            //
            //     $templateCache.remove(tmplUrl);
            //     delete $route.routes[path];
            //     delete $route.routes[path + "/"];
            // }
            //
            // let routeNames = dictKeysFromObject($route.routes);
            let i;
            //
            // // Remove existing PAPP routes
            // for (i = 0; i < routeNames.length; i++) {
            //     let routePath = routeNames[i];
            //     let lastChar = routePath[routePath.length - 1];
            //     if (routePath.indexOf("/papp_") == 0 && lastChar != "/") {
            //         removeRoute(routePath);
            //     }
            //
            // }

            for (i = 0; i < $scope.pappsMenuData.length; i++) {
                let pappMenu = $scope.pappsMenuData[i];
                $routeProvider.when(pappMenu.url, {
                    templateUrl: pappMenu.templateUrl,
                    caseInsensitiveMatch: true
                });
            }

        });


    }]);

// ------ PeekRootCtrl
peekAdminApp.controller("PeekAdmAppCtrl", ["$scope", function ($scope) {

}]);
