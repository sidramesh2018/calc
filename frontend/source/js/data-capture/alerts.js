class AlertsWidget extends window.HTMLInputElement {
  attachedCallback() {
    this.setAttribute('tabindex', '-1');
    this.focus();
  }
}

document.registerElement('alerts-widget', {
  prototype: AlertsWidget.prototype,
});
