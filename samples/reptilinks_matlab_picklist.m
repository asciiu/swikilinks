[file,path] = uigetfile('.csv');
addpath(path);

order = get_shipstation_file(file);
clear master;

[k1 k2]=size(order);  %Get the number of line items in the shipstaiton .csv file


%If an order contains multiples of the same items, a quantity count is used
%instead of listing the line item multiple times.  I list the item multiple
%times instead, so that they can later be tallied with the other line
%items. 
for(j=1:k1)
  qty=order.ItemQty(j)-1;
 
  for(jj=1:qty)
  order=[order;order(j,:)];
  end
  
end

%Find the orders that have egg added, and modify the SKU number so that
%those items appear as a unique product.  
for(j=1:k1)
    
    if(contains(order.ItemOptions(j), '1350249218131'))
     order.ItemSKU(j)   = strcat(order.ItemSKU(j),'+egg');
        
    end
     
end


% This section just counts the West coast orders and tries to estimate how
% much dry ice should be ordered for the week.  
[k1 k2]=unique(order.OrderNumber);

ice_total=0;
for(j=1:length(k2))
test=contains(string(order.CustomField1(k2(j))), 'West');
if(test)
    ice_total=ice_total+40;
else
    ice_total=ice_total+20;
end

end

test=contains(string(order.CustomField1(k2)), 'West');
[k3 k4]=find(test ==1);

west_coast_total = length(k3);
two_day_total = length(k2)-west_coast_total;



%Find all the items that do not need to be hand-made (~indicates does not
%contain)
test=~contains(order.ItemName, {'links)','Tegu'});
[k1 k2]=find(test ==1);
non_links_order=order(k1,:);

%Find all the orders that do need to be hand-made
test=contains(order.ItemName, {'links)','Tegu'});
[k1 k2]=find(test ==1);
order=order(k1,:);

%The mini and micro links are made through a seperate process, so I pull
%those out to list in a different category than the tied links
test=contains(order.ItemName, 'Mini');
[k1 k2]=find(test ==1);
mini_order=order(k1,:);

test=contains(order.ItemName, 'Micro');
[k1 k2]=find(test ==1);
mini_order=order(k1,:);

test=~contains(order.ItemName, 'Mini');
[k1 k2]=find(test ==1);
order=order(k1,:);

test=~contains(order.ItemName, 'Micro');
[k1 k2]=find(test ==1);
order=order(k1,:);

%Change the SKU and Item Names to catagorical (instead of a string), this
%allows matalb to tabulate better.  
order.ItemSKU=categorical(order.ItemSKU);
order.ItemName=categorical(order.ItemName);

mini_order.ItemSKU=categorical(mini_order.ItemSKU);
mini_order.ItemName=categorical(mini_order.ItemName);

non_links_order.ItemSKU=categorical(non_links_order.ItemSKU);
non_links_order.ItemName=categorical(non_links_order.ItemName);

%Summary just displays to the screen how many of each unique SKUs are
%listed in the table
summary(order.ItemSKU)
summary(mini_order.ItemSKU)
summary(non_links_order.ItemSKU)

%The tabulate command tallies the total quantities of each unique item,
%puts the list into a matlab structure format so that it can be more easily
%converted into HTML
order_table=tabulate(order.ItemSKU);
order_table=cell2struct(order_table,{'name';'quantity';'percent'},2);

mini_order_table=tabulate(mini_order.ItemSKU);
mini_order_table=cell2struct(mini_order_table,{'name';'quantity';'percent'},2);

non_links_table=tabulate(non_links_order.ItemSKU);
non_links_table=cell2struct(non_links_table,{'name';'quantity';'percent'},2);

%Percent variable isn't needed, so removed before printing. 
order_table=rmfield(order_table,'percent');
mini_order_table=rmfield(mini_order_table,'percent');
non_links_table=rmfield(non_links_table,'percent');


%Creates a master matalb structure to be used for HTML print subroutine
master.order_table=order_table;
master.mini_order_table=mini_order_table;
master.non_links_table=non_links_table;
master.ship_summary.ice_total=ice_total;
master.ship_summary.west_coast_total=west_coast_total;
master.ship_summary.closer_total = two_day_total;

%Create filename with current date
FileName=['Reptilinks_PL_',datestr(now, 'dd-mmm-yyyy'),'.html'];

%Create html file from the Matlab structure file. 
print2html(master,2,FileName,struct('maxel',1000,'title','Reptilinks Pick List'))



