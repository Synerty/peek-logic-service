'use strict';


// -------------------------- Placeholder Module -----------------------
define([
            // Named Depencencies

            // Unnamed Dependencies
            "angular", "jquery",
            'PeekAdmUpdatePappMod', 'PeekAdmUpdatePlatformMod',
            'PeekAdmCapabilitiesMod'
        ],
        function () {
            var peekAdmUpdateMod = angular.module('peekAdmUpdateMod',
                    ['peekAdmUpdatePappMod',
                        'peekAdmUpdatePlatformMod',
                        'peekAdmCapabilitiesMod']);

            // ------------- Root controller for this page
            peekAdmUpdateMod.controller('PeekAdmUpdatePageCtrl', ['$scope', '$location',
                function ($scope, $location) {

                    $scope.pageData = {supportExceeded: false};


                }]);


        }
);



