/**
 * Created by peek on 27/05/15.
 */
'use strict';
define([
    // Named Depencencies
    "AngFormLoadController",
    // Unnamed Dependencies
    "angular-route",
    "angular"
], function (AngFormLoadController) {
    // -------------------------- Placeholder Module -----------------------
    var peekAdmNavbarPappMenuMod = angular.module('peekAdmNavbarPappMenuMod', ['ngRoute']);
    // ------ PlaceholderCtrl
    peekAdmNavbarPappMenuMod.controller('PeekAdmNavbarPappMenuCtrl', [
        '$scope', '$route', '$templateCache',
        function ($scope, $route, $templateCache) {
            var self = this;
            self.loader = new AngFormLoadController($scope, {
                papp: "peek_server",
                key: "nav.adm.papp.list"
            }, {
                objName: 'pappsMenuData',
                dataIsArray: true
            });
        }]);
    // Add custom directive for build-navbar
    peekAdmNavbarPappMenuMod.directive('peekAdmNavbarPappMenu', function () {
        return {
            restrict: 'E',
            templateUrl: '/view/PeekAdmNavbarPappMenu.html',
            replace: true,
            controller: 'PeekAdmNavbarPappMenuCtrl',
            controllerAs: 'pappC'
        };
    });
});
//# sourceMappingURL=PeekAdmNavbarPappMenuMod.js.map