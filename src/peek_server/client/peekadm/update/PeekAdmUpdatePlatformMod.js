'use strict';


// -------------------------- Placeholder Module -----------------------
define([
            // Named Depencencies
            "AngFormLoadController",
            // Unnamed Dependencies
            "angular", "jquery", "ng-file-upload"
        ],
        function (AngFormLoadController) {
            var peekAdmUpdatePlatformMod = angular.module('peekAdmUpdatePlatformMod',
                    ['ngFileUpload']);


            // ------------- Controller for updating updater
            peekAdmUpdatePlatformMod.controller('PeekAdmUpdatePlatformCtrl', [
                '$scope', 'Upload',
                function ($scope, Upload) {
                    var self = this;

                    $scope.serverRestarting = false;

                    self.rspGood = function (data, status, headers, config) {
                        $scope.progressPercentage = '';
                        if (data.error) {
                            logError("Software Update Failed<br/>" + data.error);
                        } else {
                            $scope.serverRestarting = true;
                            logSuccess("Software Update Complete<br/>New version is "
                                    + data.message + "<br/><br/>Server will restart");
                            self.reconnectVortex();
                        }
                    };

                    self.rspBad = function (data, status, headers, config) {
                        $scope.progressPercentage = '';
                        logError("Software Update Failed<br/>" + data.error);
                    };

                    self.reconnectVortex = function () {
                        setTimeout(function () {
                            logSuccess("Server is restarting");
                        }, 3000);
                        setTimeout(function () {
                            location.reload();
                        }, 8000);
                    };

                    $scope.upload = function (files, event, rejectedFiles) {
                        if (rejectedFiles && rejectedFiles.length) {
                            logError(rejectedFiles[0].name + " does not end in .tar.bz2");
                            return;
                        }

                        if (!(files && files.length))
                            return;

                        var file = files[0];
                        Upload.upload({
                            url: '/peek_server.update.platform',
                            file: file
                        }).progress(function (evt) {
                            $scope.progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                        }).success(self.rspGood)
                                .error(self.rspBad);
                    };


                }
            ]);

        }
);



