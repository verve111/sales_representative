openerp.baron_sales_representative = function(instance) {
	
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;
	
    instance.web_graph.GraphView.include({
    	 do_search: function (domain, context, group_by) {
			this._super(domain, context, group_by);
			if (context.baron_torgovik_report && !this.custom_table) {
		        var model = new instance.web.Model("baron.partners.report");
		        var self = this;
		        model.call("get_sub_award", {context: new instance.web.CompoundContext()}).then(function(result) {
		        	//console.log(result["res"])
		        	if (!self.custom_table) {
		        		//self.custom_table = $(  );
		        		var s = "<div style='padding:10px;'><p>Процент с продаж аффилиатов:</p>"
		        			+ "<div class='row'><div class='col-sm-3'><table class='table'>"
		        			+ "    <thead> <tr> <th>Уровень</th><th>Полученный процент</th>"
		        			+ "</tr> </thead>  <tbody>";
		        		var res = result['res'];
		        		for (var i = 0; i < res.length; i++) {
		        			console.log(res[i]);
		        			s += "<tr>"
		        				+ "<td>" + res[i][1] + " (" + res[i][0] + "%)</td>"
		        				+ "<td>" + res[i][2] + "</td>"
		        				+ "</tr>"		        			
		        		}
		        		s += "    </tbody>  </table></div></div></div>";
		        		self.custom_table = $(s);
		        		self.custom_table.appendTo(self.$el);
		        	}
		        });				
				

			}
		},
    });
}
