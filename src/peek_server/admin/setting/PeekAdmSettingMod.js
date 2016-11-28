'use strict';
// -------------------------- Schedule Module -----------------------
define([
    // Named Depencencies
    "AngFormLoadController",
    // Unnamed Dependencies
    "angular", "jquery"
], function (AngFormLoadController) {
    var peekAdmSettingMod = angular.module('peekAdmSettingMod', []);
    // ------------- Root controller for this page
    peekAdmSettingMod.controller('PeekAdmSettingPageCtrl', ['$scope', '$location',
        function ($scope, $location) {
            $scope.pageData = {};
            $scope.pageData.search = null;
        }]);
    //------------- The list controller for this page ------------------
    peekAdmSettingMod.controller('PeekAdmSettingListCtrl', [
        '$scope',
        function ($scope) {
            var self = this;
            self.loader = new AngFormLoadController($scope, {
                papp: "platform",
                key: "admin.setting.data"
            }, {
                dataIsArray: true,
                actionPostfix: "Settings"
            });
            $scope.valView = function (item) {
                return { string: 'settingPropTypeString' }[item.type];
            };
        }]);
    // Add custom directive for peek_server-schedule-list
    peekAdmSettingMod.directive('peekAdmSetting', function () {
        return {
            restrict: 'E',
            templateUrl: '/view/PeekAdmSettingView.html'
        };
    });
}); // End closure
//# sourceMappingURL=PeekAdmSettingMod.js.map