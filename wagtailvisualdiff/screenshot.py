{% load staticfiles %}
{% load sc_django_tags %}


<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title>Visual Comparison for MKE</title>
		<meta name="description" content="">
		<meta name="viewport" content="width=device-width">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
	</head>
	<body>
		<div>
			<section role="main">

				<div class="col-sm-12">
					<h1>Page: <a href="{{revision1.page.url}}">{{ revision1.page }}</a></h1>
					<p><strong>These revisions were published while the screenshotservice was not active (yet). Visual Diffs require screenshots to be taken for both pages at the time of publishing.</strong></p>
				</div>
				<div class="col-sm-6">
					<p id="title1">Revision {{ revision1.id }} published by {{revision1.user.get_full_name}} on {{revision1.created_at}} -
						<a href='{% url 'wagtailrollbacks:confirm_page_reversion' revision_id=revision1.id %}' target='blank'>Revert</a> or
						<a href='{% url 'wagtailrollbacks:preview_page_version' revision_id=revision1.id %}' target='blank'>Preview</a>
					</p>
				</div>
				<div class="col-sm-6">
					<p id="title2">Revision {{ revision2.id }} published by {{revision2.user.get_full_name}} on {{revision1.created_at}} -
						<a href='{% url 'wagtailrollbacks:confirm_page_reversion' revision_id=revision2.id %}' target='blank'>Revert</a> or
						<a href='{% url 'wagtailrollbacks:preview_page_version' revision_id=revision2.id %}' target='blank'>Preview</a>
					</p>
				</div>


				<div class="col-sm-12">

					{% if difference|length > 0 %}
						{% for key, values in difference.items %}
							{% if values.1.type and not values.0.type %}
							<div class="panel panel-success">
							{% elif values.0.type and not values.1.type %}
							<div class="panel panel-danger">
							{% elif values.0.type and values.1.type %}
							<div class="panel panel-info">
							{% else %}
							<div class="panel panel-default">
							{% endif %}
								<div class="panel-heading">
    								<h3 class="panel-title">
    									Block {{ key }}:
										{% if values.1.type %}
											{{ values.1.type }}
										{% else %}
											{{ values.0.type|to_space }}
										{% endif %}
									</h3>
  								</div>
  									<table class="table">
  										<tr>
  											<th class="col-sm-6">Version {{ revision1.id }}</th>
  											<th class="col-sm-6">Version {{ revision2.id }}</th>
  										</tr>
	  									<tr>
	  										<td class="col-sm-6" style="padding:0;">
	  											{% if values.0.value.items|length != 0 %}
													<table class="table table-striped" style="margin-bottom:0px; table-layout: fixed;">
														{% for field, content in values.0.value.items%}
															<tr>
																<td class="col-sm-3">
																	{{ field|to_space }}
																</td>
																<td class="danger col-sm-9">
																	{{ content|linebreaks }}
																</td>
															</tr>

														{% endfor %}
													</table>
												{% else %}
													<h1 style="text-align: center;">NEW BLOCK</h1>
												{% endif %}

											</td>
											<td class="col-sm-6" style="padding:0;">
												{% if values.1.value.items|length != 0 %}
													<table class="table table-striped" style="margin-bottom:0px; table-layout: fixed;">
														{% for field, content in values.1.value.items%}
															<tr>
																<td class="col-sm-3">
																	{{ field|to_space }}
																</td>
																<td class="success col-sm-9">
																	{{ content|linebreaks }}
																</td>
															</tr>

														{% endfor %}
													</table>
												{% else %}
													<h1 style="text-align: center;">DELETED</h1>
												{% endif %}
											</td>
										</tr>
									</table>
							</div>


						{% endfor %}

					{% endif %}

					{% if difference|length == 0 %}
						<h2>
							No Fields have changed between these Revisions
						</h2>
					{% endif %}
				</div>

			</section>
		</div>
	</body>
</html>