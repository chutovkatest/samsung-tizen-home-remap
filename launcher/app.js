/* Minimal example only. Must be packaged/signed separately for your TV. */
(function () {
  'use strict';
  var HDMI_PORT = 2; // Change locally before building if required.
  function message(title, detail) {
    document.getElementById('state').textContent = title;
    document.getElementById('detail').textContent = detail || '';
  }
  function onError(phase, error) {
    message('Could not open HDMI ' + HDMI_PORT, phase + ': ' +
      ((error && error.name) || 'not supported on this TV'));
  }
  function openHDMI() {
    if (!window.tizen || !tizen.systeminfo || !tizen.tvwindow) {
      message('Tizen TV API unavailable', 'Use a compatible Samsung TV, not a normal browser.');
      return;
    }
    try {
      tizen.systeminfo.getPropertyValue('VIDEOSOURCE', function (info) {
        var inputs = info.connected || [];
        var source = inputs.filter(function (input) {
          return input.type === 'HDMI' && Number(input.number) === HDMI_PORT;
        })[0];
        if (!source) {
          message('HDMI ' + HDMI_PORT + ' is not detected',
                  'Connect a device or set the correct HDMI_PORT.');
          return;
        }
        tizen.tvwindow.setSource(source, function () {
          tizen.tvwindow.show(function () {
            message('HDMI ' + HDMI_PORT + ' is active', '');
          }, function (error) { onError('show', error); },
          ['0%', '0%', '100%', '100%'], 'MAIN', 'BEHIND');
        }, function (error) { onError('setSource', error); });
      }, function (error) { onError('getPropertyValue', error); });
    } catch (error) { onError('Tizen exception', error); }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', openHDMI);
  } else { openHDMI(); }
}());
