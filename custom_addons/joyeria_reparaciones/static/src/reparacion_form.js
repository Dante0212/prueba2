odoo.define('joyeria_reparaciones.reparacion_form', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const viewRegistry = require('web.view_registry');
    const FormView = require('web.FormView');

    const ReparacionFormController = FormController.extend({
        _onFieldChanged: function (event) {
            this._super.apply(this, arguments);

            if (event.data.changes.servicio !== undefined) {
                this._updateServicioVisibility(event.data.changes.servicio);
            }
        },

        _updateServicioVisibility: function (servicio) {
            const $form = this.$el;
            const mostrarReparacion = servicio === 'reparacion';
            const mostrarFabricacion = servicio === 'fabricacion';

            $form.find('[name="tipo_joya"]').closest('.o_field_widget').toggle(mostrarReparacion);
            $form.find('[name="n_cm_reparacion"]').closest('.o_field_widget').toggle(mostrarReparacion);
            $form.find('[name="n_cm_fabricacion"]').closest('.o_field_widget').toggle(mostrarFabricacion);
        },

        _render: function () {
            const self = this;
            return this._super.apply(this, arguments).then(function () {
                const servicio = self.model.get(self.handle, { raw: true }).data.servicio;
                self._updateServicioVisibility(servicio);
            });
        },
    });

    const ReparacionFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: ReparacionFormController,
        }),
    });

    viewRegistry.add('reparacion_form_js', ReparacionFormView);
});
