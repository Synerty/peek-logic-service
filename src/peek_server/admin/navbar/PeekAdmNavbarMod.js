/// <amd-dependency path="angular"/>
'use strict';
define([
    // Named Dependencies
    "AngFormLoadController",
    // Unnamed Dependencies
    "PeekAdmNavbarPappMenuMod",
    "angular", "jquery"], function (AngFormLoadController) {
    // -------------------------- Navbar Module -----------------------
    var peekAdmNavbarMod = angular.module('peekAdmNavbarMod', [
        'peekAdmNavbarPappMenuMod'
    ]);
    // ------ BuildNavbarCtrl
    peekAdmNavbarMod.controller('PeekAdmNavbarCtrl', [
        '$scope',
        '$location',
        function ($scope, $location) {
            var self = this;
            var s = $scope;
            $scope.wereAt = function (path) {
                return $location.absUrl().endsWith(path)
                    || ($location.path().startsWith(path) && !$location.path().startsWith(path + '/'));
            };
            new AngFormLoadController($scope, {
                papp: 'platform',
                key: "admin.navbar.data"
            }, {
                objName: "navData"
            });
        }]);
    // Add custom directive for peek_server-navbar
    peekAdmNavbarMod.directive('peekAdmNavbar', function () {
        return {
            restrict: 'E',
            templateUrl: '/view/PeekAdmNavbarView.html'
        };
    });
});
//# sourceMappingURL=PeekAdmNavbarMod.js.map